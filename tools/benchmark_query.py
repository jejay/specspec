"""Benchmark fresh query processes and profile one invocation (no result cache).

Run in the development environment, e.g.:
  python tools/benchmark_query.py --root . --runs 3 --output .specspec-local/query-bench.json
OS caches are not flushed. Captured stdout excludes terminal rendering costs.
"""

from __future__ import annotations

import argparse
import cProfile
import hashlib
import io
import json
import platform
import pstats
import statistics
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from unittest.mock import patch


def benchmark(
    root: Path,
    runs: int,
    output: Path,
    *,
    node_id=None,
    min_distance=None,
    max_distance=None,
    influence=None,
    with_ancestors=False,
) -> dict:
    root = root.resolve()
    selection = {
        key: value
        for key, value in {
            "node_id": node_id,
            "min_distance": min_distance,
            "max_distance": max_distance,
            "influence": influence,
            "with_ancestors": with_ancestors or None,
        }.items()
        if value is not None
    }
    arguments = [node_id] if node_id is not None else []
    for key, value in selection.items():
        if key != "node_id":
            option = "--" + key.replace("_", "-")
            arguments.extend([option] if value is True else [option, value])
    timings = {}
    for kind, options in (("text", []), ("json", ["--json"])):
        seconds, digests, sizes = [], [], []
        for _ in range(runs):
            started = time.perf_counter()
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "specspec",
                    "--root",
                    str(root),
                    "query",
                    *arguments,
                    *options,
                ],
                capture_output=True,
                timeout=120,
            )
            if result.returncode:
                raise RuntimeError(result.stderr.decode("utf8", errors="replace"))
            seconds.append(time.perf_counter() - started)
            digests.append(hashlib.sha256(result.stdout).hexdigest())
            sizes.append(len(result.stdout))
        timings[kind] = {
            "seconds": seconds,
            "median_seconds": statistics.median(seconds),
            "output_sha256": digests,
            "output_bytes": sizes,
        }

    from specspec.query import read_query, render_query
    from specspec.wire import comparison

    processes = Counter()
    original = subprocess.Popen

    def counted(command, *args, **kwargs):
        family = next(
            (
                part
                for part in command
                if part in {"cat-file", "rev-parse", "ls-tree", "ls-files", "diff", "log"}
            ),
            str(command[0]),
        )
        if family == "cat-file":
            family += " " + command[-1]
        processes[family] += 1
        return original(command, *args, **kwargs)

    profile = cProfile.Profile()
    with patch("subprocess.Popen", counted):
        profile.enable()
        started = time.perf_counter()
        query = read_query(root, **selection)
        read_seconds = time.perf_counter() - started
        started = time.perf_counter()
        render_query(query)
        render_seconds = time.perf_counter() - started
        started = time.perf_counter()
        json.dumps(comparison(query.result), ensure_ascii=False)
        json_seconds = time.perf_counter() - started
        profile.disable()
    report = {
        "python": sys.version,
        "platform": platform.platform(),
        "root": str(root),
        "runs": runs,
        "query": selection,
        "scope": (
            "Fresh CLI processes; OS caches not flushed; captured stdout. "
            "Profile includes instrumentation overhead."
        ),
        "cli": timings,
        "profile": {
            "read_seconds": read_seconds,
            "render_seconds": render_seconds,
            "json_seconds": json_seconds,
            "git_processes": dict(processes),
        },
        "nodes": len(query.target.nodes),
        "source_rows": len(query.result["source_resolutions"]),
        "selection": query.result.get("selection"),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf8")
    profile.dump_stats(output.with_suffix(".prof"))
    text = io.StringIO()
    pstats.Stats(profile, stream=text).sort_stats("cumulative").print_stats(40)
    output.with_suffix(".profile.txt").write_text(text.getvalue(), encoding="utf8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--node-id")
    parser.add_argument("--min-distance")
    parser.add_argument("--max-distance")
    parser.add_argument("--influence")
    parser.add_argument("--with-ancestors", action="store_true")
    options = parser.parse_args()
    if options.runs < 1:
        parser.error("--runs must be positive")
    print(
        json.dumps(
            benchmark(
                options.root,
                options.runs,
                options.output,
                node_id=options.node_id,
                min_distance=options.min_distance,
                max_distance=options.max_distance,
                influence=options.influence,
                with_ancestors=options.with_ancestors,
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

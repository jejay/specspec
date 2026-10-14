"""Read-only Git source addresses, bounded region mapping and explicit capture.

Blob IDs are content addresses, not node fingerprints or reachability edges.
No operation here writes objects, refs, indexes, commits or source files.
"""

from __future__ import annotations

import difflib
import os
import subprocess
from pathlib import Path
from typing import Any

from .git import repository_paths, resolve_commit
from .model import Diagnostic, SpecError, SpecNode
from .source_schema import validate_source

MAX_BYTES = 2 * 1024 * 1024
MAX_TOTAL_BYTES = 32 * 1024 * 1024
MAX_LINES = 10_000
MAX_CELLS = 20_000_000
BAD_OUTCOMES = {"conflict", "missing", "ambiguous", "unavailable"}


def git_environment():
    return {
        **os.environ,
        "GIT_NO_LAZY_FETCH": "1",
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_ALLOW_PROTOCOL": "",
    }


def run_git(root: Path, *args: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "--literal-pathspecs", *args],
            capture_output=True,
            timeout=20,
            env=git_environment(),
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise SpecError([Diagnostic("SOURCE_GIT", str(error))]) from error
    if result.returncode or len(result.stdout) > MAX_TOTAL_BYTES:
        raise SpecError(
            [Diagnostic("SOURCE_GIT", "Local Git source read failed or exceeded its budget.")]
        )
    return result.stdout


def text_lines(raw: bytes) -> list[str]:
    if (
        len(raw) > MAX_BYTES
        or b"\0" in raw
        or raw.startswith(b"version https://git-lfs.github.com/spec/")
    ):
        raise ValueError("Line targets require bounded UTF-8 text, not binary/LFS pointer data.")
    lines = raw.decode("utf-8-sig").splitlines()
    if len(lines) > MAX_LINES:
        raise ValueError(f"Source exceeds the {MAX_LINES}-line resolution budget.")
    return lines


def merged(intervals: list[list[int]]) -> list[list[int]]:
    result: list[list[int]] = []
    for start, end in sorted(intervals):
        if result and start <= result[-1][1] + 1:
            result[-1][1] = max(result[-1][1], end)
        else:
            result.append([start, end])
    return result


def occurrences(haystack: list[str], needle: list[str]) -> list[int]:
    return [
        i for i in range(len(haystack) - len(needle) + 1) if haystack[i : i + len(needle)] == needle
    ]


def map_regions(old: list[str], new: list[str], ranges: list[list[int]], mode: str) -> dict:
    if any(end > len(old) for _, end in ranges):
        raise ValueError("Range exceeds its anchored source snapshot.")
    if len(old) * len(new) > MAX_CELLS:
        raise ValueError("Source pair exceeds the bounded diff budget.")
    if old == new:
        return {"outcome": "resolved", "ranges": ranges, "changed": False}
    opcodes = difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes()
    all_ranges, changed, ambiguity = [], False, False
    for start, end in ranges:
        a, b = start - 1, end
        pieces, touched = [], False
        for tag, i, stop, j, target_stop in opcodes:
            lo, hi = max(a, i), min(b, stop)
            if tag == "equal" and lo < hi:
                pieces.append([j + lo - i + 1, j + hi - i])
            elif tag == "insert" and a < i < b:
                touched = True
                if mode == "expanding":
                    pieces.append([j + 1, target_stop])
            elif tag in {"replace", "delete"} and lo < hi:
                touched = True
                if mode == "expanding" and tag == "replace":
                    if i < a or stop > b:
                        ambiguity = True  # No justified boundary inside a replacement block.
                    else:
                        pieces.append([j + 1, target_stop])
        # An exact uniquely contextualized block can follow an intra-file move.
        needle = old[a:b]
        hits = occurrences(new, needle)
        if len(hits) > 1:
            left, right = old[max(0, a - 2) : a], old[b : b + 2]
            contextual = [
                p
                for p in hits
                if new[max(0, p - len(left)) : p] == left
                and new[p + len(needle) : p + len(needle) + len(right)] == right
            ]
            if len(contextual) != 1:
                ambiguity = True
            elif not touched:
                pieces = [[contextual[0] + 1, contextual[0] + len(needle)]]
        if touched and len(occurrences(old, needle)) > 1:
            ambiguity = True  # Deleting one copy must not retarget another survivor.
        if not pieces and len(hits) == 1 and not ambiguity:
            pieces = [[hits[0] + 1, hits[0] + len(needle)]]
            touched = False
        changed |= touched
        # Merge only within each original region: do not absorb gaps between selections.
        all_ranges.extend(merged(pieces))
    outcome = (
        "ambiguous"
        if ambiguity
        else "conflict"
        if changed and mode == "strict"
        else "missing"
        if not all_ranges
        else "modified"
        if changed
        else "resolved"
    )
    return {"outcome": outcome, "ranges": all_ranges, "changed": changed}


class SourceReader:
    """One request: cache Git listings/blobs/mappings; batch anchor object reads."""

    def __init__(self, root: Path, *, ref: str | None = None, staged: bool = False):
        if ref and staged:
            raise ValueError("Do not combine a revision with --staged.")
        self.root = root.resolve()
        self.ref, self.staged = ref, staged
        self.target = "index" if staged else ref or "worktree"
        self.repo: Path | None = None
        self.prefix = ""
        self.commit: str | None = None
        self.entries: dict[str, tuple[str, str]] = {}
        self.blobs: dict[str, bytes | str] = {}
        self.mappings: dict[tuple, dict] = {}
        self.data_cache: dict[str, bytes] = {}
        self.read_bytes = 0
        self.renames: dict[tuple[str, str], list[str]] = {}
        self.retained: set[str] | None = None
        try:
            self.repo, prefix = repository_paths(self.root)
            self.prefix = prefix.removesuffix("_specspec")
            if ref:
                self.commit = resolve_commit(self.repo, ref)
                data = run_git(self.repo, "ls-tree", "-r", "-z", self.commit)
            elif staged:
                data = run_git(self.repo, "ls-files", "--stage", "-z")
            else:
                data = run_git(self.repo, "ls-files", "--stage", "-z")
            for record in data.split(b"\0"):
                if not record:
                    continue
                metadata, path = record.split(b"\t", 1)
                fields = metadata.decode().split()
                mode, oid = (fields[0], fields[2]) if ref else (fields[0], fields[1])
                if not ref and fields[2] != "0":
                    continue
                self.entries[path.decode("utf-8", errors="surrogateescape")] = (mode, oid)
        except SpecError as error:
            if ref or staged:
                raise
            self.git_error = str(error)
            self.repo = None  # Whole-file and working-text links still work without Git.

    def batch(self, ids: set[str]) -> None:
        pending = sorted(ids - self.blobs.keys())
        if not pending:
            return
        if self.repo is None:
            for oid in pending:
                self.blobs[oid] = "Git repository/object database is unavailable."
            return

        def request(arguments, payload):
            try:
                result = subprocess.run(
                    ["git", "-C", str(self.repo), *arguments],
                    input=payload,
                    capture_output=True,
                    timeout=20,
                    env=git_environment(),
                    check=True,
                )
            except (subprocess.SubprocessError, OSError) as error:
                raise ValueError(f"Git object read failed: {error}") from error
            return result.stdout

        metadata = request(["cat-file", "--batch-check"], ("\n".join(pending) + "\n").encode())
        accepted, total = [], 0
        for oid, row in zip(pending, metadata.splitlines(), strict=True):
            fields = row.decode().split()
            if len(fields) != 3 or fields[1] != "blob":
                self.blobs[oid] = "Anchor object is missing or is not a blob."
                continue
            size = int(fields[2])
            total += size
            if size > MAX_BYTES or total > MAX_TOTAL_BYTES:
                self.blobs[oid] = "Source object read budget exceeded."
            else:
                accepted.append(oid)
        if accepted:
            data = request(["cat-file", "--batch"], ("\n".join(accepted) + "\n").encode())
            offset = 0
            for oid in accepted:
                end = data.index(b"\n", offset)
                size = int(data[offset:end].split()[2])
                self.blobs[oid] = data[end + 1 : end + 1 + size]
                offset = end + size + 2

    def blob(self, oid: str) -> bytes:
        self.batch({oid})
        data = self.blobs[oid]
        if isinstance(data, str):
            raise ValueError(data)
        return data

    def safe_file(self, path: str) -> Path:
        target = self.root / path
        if target.is_symlink() or not target.resolve().is_relative_to(self.root):
            raise ValueError("Source path resolves through a symlink/escape.")
        return target

    def data(self, path: str) -> bytes:
        if path not in self.data_cache:
            value = self.read_data(path)
            if self.read_bytes + len(value) > MAX_TOTAL_BYTES:
                raise ValueError("Source request exceeds its aggregate read budget.")
            self.data_cache[path] = value
            self.read_bytes += len(value)
        return self.data_cache[path]

    def read_data(self, path: str) -> bytes:
        self.safe_file(path)  # Also refuse current workspace symlink escapes for revision links.
        if self.ref or self.staged:
            entry = self.entries.get(self.prefix + path)
            if not entry:
                raise FileNotFoundError(path)
            mode, oid = entry
            if mode not in {"100644", "100755"}:
                raise ValueError(
                    "Git source entry must be a regular file, not a symlink/submodule."
                )
            return self.blob(oid)
        target = self.safe_file(path)
        if target.stat().st_size > MAX_BYTES:
            raise ValueError("Source exceeds the read budget.")
        return target.read_bytes()

    def paths_for(self, source: dict) -> list[str]:
        path, oid = source["path"], source["blob"]
        # The same path is authoritative; do not prefer an unrelated identical copy.
        try:
            self.data(path)
            return [path]
        except FileNotFoundError:
            pass
        candidates = [
            p[len(self.prefix) :]
            for p, (mode, value) in self.entries.items()
            if p.startswith(self.prefix) and mode in {"100644", "100755"} and value == oid
        ]
        if candidates:
            return candidates
        if self.repo is None:
            return []
        key = (path, oid)
        if key in self.renames:
            return self.renames[key]
        # Blob alone has no ancestry; find retained occurrences at the original path,
        # then ask Git for rename evidence relative to the requested target.
        history = (
            run_git(
                self.repo,
                "log",
                "--all",
                "--format=%H",
                f"--find-object={oid}",
                "--",
                self.prefix + path,
            )
            .decode()
            .splitlines()
        )
        if len(history) > 128:
            raise ValueError("Rename history exceeds the bounded search budget.")
        found = set()
        for base in history:
            original = run_git(self.repo, "ls-tree", "-z", base, "--", self.prefix + path)
            if not original or original.split(b"\t", 1)[0].split()[-1].decode() != oid:
                continue
            args = [
                "diff",
                "--no-ext-diff",
                "--no-textconv",
                "--name-status",
                "-z",
                "--find-renames",
                base,
            ]
            if self.commit:
                args.append(self.commit)
            elif self.staged:
                args.append("--cached")
            rows = run_git(self.repo, *args).split(b"\0")
            i = 0
            while i < len(rows) and rows[i]:
                kind = rows[i].decode()
                i += 1
                old = rows[i].decode("utf-8", errors="surrogateescape")
                i += 1
                if kind.startswith(("R", "C")):
                    new = rows[i].decode("utf-8", errors="surrogateescape")
                    i += 1
                    if old == self.prefix + path and new.startswith(self.prefix):
                        found.add(new[len(self.prefix) :])
        self.renames[key] = sorted(found)
        return self.renames[key]

    def resolve(self, source: dict, *, retention: bool = False) -> dict:
        result: dict[str, Any] = {
            "path": source["path"],
            "target": self.target,
            "mode": source.get("mode", "file"),
            "ranges": [],
        }
        try:
            validate_source(source)
            if "blob" not in source:
                target = self.safe_file(source["path"])
                if self.ref or self.staged:
                    entry = self.entries.get(self.prefix + source["path"])
                    if not entry:
                        raise FileNotFoundError(source["path"])
                    if entry[0] not in {"100644", "100755"}:
                        raise ValueError("Source Git entry is not a regular file.")
                elif not target.is_file():
                    raise FileNotFoundError(source["path"])
                return {**result, "outcome": "file", "changed": False}
            old = text_lines(self.blob(source["blob"]))
            candidates = self.paths_for(source)
            if len(candidates) != 1:
                return {
                    **result,
                    "outcome": "ambiguous" if candidates else "missing",
                    "message": "No unique source file location.",
                    "candidates": candidates,
                }
            path = candidates[0]
            new = text_lines(self.data(path))
            key = (source["blob"], path, repr(source["ranges"]), source["mode"])
            if key not in self.mappings:
                self.mappings[key] = map_regions(old, new, source["ranges"], source["mode"])
            result.update(self.mappings[key])
            result["path"] = path
            result["relocated"] = path != source["path"] or result["ranges"] != source["ranges"]
            if retention and not self.is_retained(source["blob"]):
                result.update(
                    outcome="unavailable",
                    message=(
                        "Blob is not retained by history or the staged source tree; "
                        "Markdown IDs do not retain objects."
                    ),
                )
            return result
        except FileNotFoundError:
            return {**result, "outcome": "missing", "message": "Source file is missing."}
        except (ValueError, UnicodeError, OSError, SpecError) as error:
            return {**result, "outcome": "unavailable", "message": str(error)}

    def is_retained(self, oid: str) -> bool:
        if any(
            mode in {"100644", "100755"} and value == oid for mode, value in self.entries.values()
        ):
            return True
        if self.retained is None:
            if self.repo is None:
                return False
            data = run_git(self.repo, "rev-list", "--objects", "--all", "--no-object-names")
            if len(data) > MAX_TOTAL_BYTES:
                raise ValueError("Reachability check exceeds its budget.")
            self.retained = set(data.decode().splitlines())
        return oid in self.retained

    def capture(
        self, path: str, ranges: list[list[int]], mode: str, symbol: str | None = None
    ) -> dict:
        if not (self.ref or self.staged):
            raise ValueError("Capture requires a committed revision or the explicit staged index.")
        entry = self.entries.get(self.prefix + path)
        if not entry:
            raise ValueError("Stage or commit the source file before capture.")
        source = {"path": path, "blob": entry[1], "mode": mode, "ranges": ranges}
        if symbol is not None:
            source["symbol"] = symbol
        validate_source(source)
        lines = text_lines(self.data(path))
        if any(end > len(lines) for _, end in ranges):
            raise ValueError("Range exceeds captured source content.")
        return source


def resolve_nodes(
    root: Path, nodes: list[SpecNode], *, ref=None, staged=False, retention=False
) -> list[dict]:
    reader = SourceReader(root, ref=ref, staged=staged)
    reader.batch({s["blob"] for n in nodes for s in n.sources if "blob" in s})
    return [
        {"id": n.id, "source": i, **reader.resolve(s, retention=retention)}
        for n in nodes
        for i, s in enumerate(n.semantic()["sources"], 1)
    ]


def check_results(results: list[dict]) -> list[Diagnostic]:
    return [
        Diagnostic(
            "SOURCE_LINK",
            f"Source {r['source']}: {r['outcome']}. {r.get('message', '')}",
            r["path"],
            r["id"],
        )
        for r in results
        if r["outcome"] in BAD_OUTCOMES
    ]

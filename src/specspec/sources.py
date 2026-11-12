"""Read-only Git source addresses, bounded region mapping and explicit capture.

Blob IDs are content addresses, not node fingerprints or reachability edges.
No operation here writes objects, refs, indexes, commits or source files.
"""

from __future__ import annotations

import difflib
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from .git import repository_paths, resolve_commit
from .git_process import GitProcessError, pathspec_chunks, run_git_process
from .model import Diagnostic, SpecError, SpecNode
from .node_text import logical_lines
from .source_schema import validate_source

MAX_BYTES = 2 * 1024 * 1024
MAX_TOTAL_BYTES = 32 * 1024 * 1024
MAX_GIT_OUTPUT = 32 * 1024 * 1024
MAX_LINES = 10_000
MAX_CELLS = 20_000_000
GIT_TIMEOUT = 20
BAD_OUTCOMES = {"conflict", "missing", "ambiguous", "unavailable"}


def run_git(root: Path, *args: str) -> bytes:
    try:
        result = run_git_process(
            root, "--literal-pathspecs", *args, timeout=GIT_TIMEOUT, max_output=MAX_GIT_OUTPUT
        )
    except GitProcessError as error:
        raise SpecError([Diagnostic("SOURCE_GIT", str(error))]) from error
    if result.returncode:
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
    # Editors, grep and Git agree on LF/CRLF (and CR) lines; form feeds and Unicode
    # separators stay line content, so captured ranges match their line numbers.
    lines = logical_lines(raw.decode("utf-8-sig"))
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
    if old == new:
        # Identical lines need no diff, so the pair budget applies only to real diffs.
        return {"outcome": "resolved", "ranges": ranges, "changed": False}
    if len(old) * len(new) > MAX_CELLS:
        raise ValueError("Source pair exceeds the bounded diff budget.")
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
    """One request: cache Git entries/blobs/mappings; batch path and anchor lookups."""

    def __init__(self, root: Path, *, ref: str | None = None, staged: bool = False):
        if ref and staged:
            raise ValueError("Do not combine a revision with --staged.")
        self.root = root.resolve()
        self.ref, self.staged = ref, staged
        self.target = "index" if staged else ref or "worktree"
        self.repo: Path | None = None
        self.prefix = ""
        self.commit: str | None = None
        # Referenced paths resolve through bounded pathspec lookups. The complete
        # tree/index loads only to search other paths for an anchored blob.
        self.entries: dict[str, tuple[str, str]] = {}
        self.lookups: dict[str, str | None] = {}
        self.listed = False
        self.listing_error: str | None = None
        self.blobs: dict[str, bytes | str] = {}
        self.mappings: dict[tuple, dict] = {}
        self.data_cache: dict[str, bytes] = {}
        self.read_bytes = 0
        self.renames: dict[tuple[str, str], list[str]] = {}
        self.retained: set[str] | None = None
        try:
            self.repo, prefix = repository_paths(self.root)
            self.prefix = prefix.removesuffix(".specspec")
            if ref:
                self.commit = resolve_commit(self.repo, ref)
        except SpecError as error:
            if ref or staged:
                raise
            self.git_error = str(error)
            self.repo = None  # Whole-file and working-text links still work without Git.

    def record(self, data: bytes) -> None:
        for record in data.split(b"\0"):
            if not record:
                continue
            metadata, path = record.split(b"\t", 1)
            fields = metadata.decode().split()
            if self.ref:
                if fields[1] == "tree":
                    continue  # A directory path names no file entry.
                mode, oid = fields[0], fields[2]
            elif fields[2] != "0":
                continue
            else:
                mode, oid = fields[0], fields[1]
            self.entries[path.decode("utf-8", errors="surrogateescape")] = (mode, oid)

    def lookup(self, paths: Iterable[str]) -> None:
        """Resolve these project paths' revision/index entries in bounded batches."""
        if self.listed or self.repo is None:
            return
        names = sorted({self.prefix + path for path in paths} - self.lookups.keys())
        command = (
            ["ls-tree", "-z", self.commit, "--"]
            if self.commit
            else ["ls-files", "--stage", "-z", "--"]
        )
        for chunk in pathspec_chunks(names):
            try:
                self.record(run_git(self.repo, *command, *chunk))
                error = None
            except (SpecError, ValueError, IndexError, UnicodeError) as failure:
                error = f"Git source entry lookup failed: {failure}"
            self.lookups.update(dict.fromkeys(chunk, error))

    def entry(self, path: str) -> tuple[str, str] | None:
        name = self.prefix + path
        if not self.listed:
            self.lookup([path])
            if error := self.lookups.get(name):
                raise ValueError(error)
        return self.entries.get(name)

    def listing(self) -> dict[str, tuple[str, str]]:
        """Load the whole target tree/index once, only for blob-identity searches."""
        if self.listing_error is not None:
            raise ValueError(self.listing_error)
        if not self.listed and self.repo is not None:
            command = (
                ["ls-tree", "-r", "-z", self.commit]
                if self.commit
                else ["ls-files", "--stage", "-z"]
            )
            try:
                self.record(run_git(self.repo, *command))
            except (SpecError, ValueError, IndexError, UnicodeError) as error:
                self.listing_error = f"Git source listing failed: {error}"
                raise ValueError(self.listing_error) from error
            self.listed = True
        return self.entries

    def batch(self, ids: set[str]) -> None:
        pending = sorted(ids - self.blobs.keys())
        if not pending:
            return
        if self.repo is None:
            for oid in pending:
                self.blobs[oid] = "Git repository/object database is unavailable."
            return
        try:
            self.read_objects(pending)
        except (SpecError, ValueError, IndexError, UnicodeError, OSError) as error:
            # Failed requests become per-object outcomes, not command-level failures.
            for oid in pending:
                self.blobs.setdefault(oid, f"Git object read failed: {error}")

    def read_objects(self, pending: list[str]) -> None:
        def request(arguments, payload):
            try:
                result = run_git_process(self.repo, *arguments, input=payload, timeout=GIT_TIMEOUT)
            except GitProcessError as error:
                raise ValueError(str(error)) from error
            if result.returncode:
                raise ValueError(
                    result.stderr.decode("utf-8", errors="replace").strip()
                    or f"git cat-file exited with status {result.returncode}."
                )
            return result.stdout

        metadata = request(["cat-file", "--batch-check"], ("\n".join(pending) + "\n").encode())
        accepted, total = [], 0
        for oid, row in zip(pending, metadata.splitlines(), strict=True):
            fields = row.decode().split()
            if len(fields) != 3 or fields[1] != "blob":
                self.blobs[oid] = "Anchor object is missing or is not a blob."
                continue
            size = int(fields[2])
            if size > MAX_BYTES or total + size > MAX_TOTAL_BYTES:
                self.blobs[oid] = "Source object read budget exceeded."
            else:
                accepted.append(oid)
                total += size
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
            entry = self.entry(path)
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
            for p, (mode, value) in self.listing().items()
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
                    entry = self.entry(source["path"])
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
        def present(entries):
            return any(
                mode in {"100644", "100755"} and value == oid for mode, value in entries.values()
            )

        # Referenced entries already retain unchanged anchors; only others need the
        # complete target tree/index before the reachability walk.
        if present(self.entries) or present(self.listing()):
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
        entry = self.entry(path)
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
    reader.lookup(s["path"] for n in nodes for s in n.sources)
    reader.batch({s["blob"] for n in nodes for s in n.sources if "blob" in s})
    return [
        {"id": n.id, "source": i, **reader.resolve(s, retention=retention)}
        for n in nodes
        for i, s in enumerate(n.semantic()["sources"], 1)
    ]


def link_explanation(result: dict) -> str:
    """Say what a bad source outcome means and what brings the link back in line."""
    reanchor = (
        f"Align node {result['id']}'s explanation with {result['path']}, stage the code, "
        f"then run specspec sources reanchor {result['id']} --source {result['source']} "
        "--staged."
    )
    if result["outcome"] == "conflict":
        return (
            "The linked lines changed since they were captured, and strict links do not "
            "follow edits. " + reanchor
        )
    if result["outcome"] == "ambiguous":
        found = result.get("message") or "The linked lines now match several places."
        return f"{found} {reanchor}"
    return result.get("message", "")


def check_results(results: list[dict]) -> list[Diagnostic]:
    return [
        Diagnostic(
            "SOURCE_LINK",
            f"Source {r['source']}: {r['outcome']}. {link_explanation(r)}".rstrip(),
            r["path"],
            r["id"],
        )
        for r in results
        if r["outcome"] in BAD_OUTCOMES
    ]

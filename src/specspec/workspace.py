"""Filesystem snapshots and recoverable, tool-managed edits."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import shutil
import unicodedata
import uuid
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath
from typing import Any

from .format import parse_node, read_document, serialize
from .graph import Graph, build_graph
from .model import FORMAT_VERSION, Diagnostic, SpecError, SpecNode, fingerprint

SPEC_DIR = "_specspec"
STATE_DIR = ".specspec-local"


@dataclass
class Snapshot:
    root: Path
    files: dict[str, bytes]
    nodes: list[SpecNode]
    diagnostics: list[Diagnostic]
    graph: Graph | None

    @property
    def valid(self) -> bool:
        return not any(d.severity == "error" for d in self.diagnostics)

    @property
    def fingerprint(self) -> str:
        return fingerprint(self.nodes)

    def require_valid(self) -> Graph:
        if not self.valid or self.graph is None:
            raise SpecError(
                self.diagnostics or [Diagnostic("EMPTY", "No specification graph exists.")]
            )
        return self.graph

    @property
    def format_version(self) -> int | None:
        return next((node.format_version for node in self.nodes if node.type == "manifesto"), None)

    def to_dict(self) -> dict[str, Any]:
        return {
            "fingerprint": self.fingerprint,
            "format_version": self.format_version,
            "nodes": [node.to_dict() for node in sorted(self.nodes, key=lambda n: n.id)],
            "edges": self.graph.edges() if self.graph else [],
            "valid": self.valid,
        }


def discover_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).absolute()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        directory = candidate / SPEC_DIR
        if directory.exists() or directory.is_symlink():
            return candidate
    raise SpecError(
        [Diagnostic("WORKSPACE", "No _specspec directory found; run specspec init.")], 2
    )


def runtime_diagnostics(root: Path) -> list[Diagnostic]:
    state = root / STATE_DIR
    if state.is_symlink() or (state.exists() and not state.is_dir()):
        return [Diagnostic("STATE", "Runtime state must be a real directory.", STATE_DIR)]
    if state.exists() and any(entry.is_symlink() for entry in state.iterdir()):
        return [Diagnostic("STATE", "Runtime state contains a forbidden symlink.", STATE_DIR)]
    if (state / "journal.json").exists():
        return [Diagnostic("RECOVERY", "An interrupted edit needs specspec recover.", STATE_DIR)]
    if (state / "lock").exists():
        return [
            Diagnostic(
                "LOCKED", "An edit is in progress or a stale lock needs recovery.", STATE_DIR
            )
        ]
    if state.exists() and any(state.glob("stage-*")):
        return [Diagnostic("RECOVERY", "Unfinished staging needs specspec recover.", STATE_DIR)]
    return []


def read_files(root: Path) -> tuple[dict[str, bytes], list[Diagnostic]]:
    directory = root / SPEC_DIR
    diagnostics: list[Diagnostic] = []
    files: dict[str, bytes] = {}
    if directory.is_symlink() or not directory.is_dir():
        return files, [Diagnostic("DIRECTORY", "_specspec must be a real directory.", SPEC_DIR)]
    for entry in sorted(directory.iterdir()):
        path = f"{SPEC_DIR}/{entry.name}"
        if entry.is_symlink() or not entry.is_file() or entry.suffix != ".md":
            diagnostics.append(
                Diagnostic("ENTRY", "Only direct, non-symlink Markdown nodes are allowed.", path)
            )
        else:
            try:
                if entry.stat().st_size > 1024 * 1024:
                    diagnostics.append(Diagnostic("FORMAT", "Node exceeds the 1 MiB limit.", path))
                else:
                    files[path] = entry.read_bytes()
            except OSError as error:
                diagnostics.append(Diagnostic("IO", str(error), path))
    return files, diagnostics


def snapshot_from_files(
    root: Path,
    files: dict[str, bytes],
    diagnostics: list[Diagnostic] | None = None,
    *,
    check_sources: bool = False,
    allow_empty: bool = False,
) -> Snapshot:
    errors = list(diagnostics or [])
    documents: dict[str, tuple[Any, str]] = {}
    for path, raw in sorted(files.items()):
        if len(PurePosixPath(path).parts) != 2 or not path.startswith(SPEC_DIR + "/"):
            errors.append(Diagnostic("ENTRY", "Nested specification files are not allowed.", path))
            continue
        try:
            documents[path] = read_document(raw, path)
        except SpecError as error:
            errors.extend(error.diagnostics)
    if not files and allow_empty and not errors:
        return Snapshot(root, files, [], [], None)
    manifestos = [
        (path, data) for path, (data, _) in documents.items() if data.get("type") == "manifesto"
    ]
    if len(manifestos) != 1:
        errors.append(Diagnostic("ROOT", "Exactly one parseable manifesto is required."))
        return Snapshot(root, files, [], errors, None)
    manifesto_path, manifesto_data = manifestos[0]
    version = manifesto_data.get("format_version")
    if type(version) is not int or version not in {1, FORMAT_VERSION}:
        errors.append(
            Diagnostic(
                "VERSION",
                f"Manifesto must declare supported format_version: 1 or {FORMAT_VERSION}.",
                manifesto_path,
            )
        )
        return Snapshot(root, files, [], errors, None)
    nodes: list[SpecNode] = []
    seen: dict[str, str] = {}
    duplicates = False
    for path, (data, body) in documents.items():
        try:
            node = parse_node(data, body, path, version=version)
            if node.id in seen:
                errors.append(
                    Diagnostic(
                        "DUPLICATE", f"Duplicate ID also present in {seen[node.id]}.", path, node.id
                    )
                )
                duplicates = True
            seen[node.id] = path
            nodes.append(node)
            if node.managed_hash != node.digest():
                errors.append(
                    Diagnostic(
                        "INTEGRITY",
                        "Unmanaged content change detected; restore it and edit through specspec.",
                        path,
                        node.id,
                    )
                )
        except SpecError as error:
            errors.extend(error.diagnostics)
    graph = None
    if not duplicates and len(nodes) == len(files):
        graph, graph_errors = build_graph(nodes)
        errors.extend(graph_errors)
    if check_sources:
        resolved_root = root.resolve()
        for node in nodes:
            for source in node.sources:
                target = (root / source["path"]).resolve()
                if not target.is_relative_to(resolved_root):
                    errors.append(
                        Diagnostic(
                            "SOURCE_ESCAPE",
                            "Source resolves outside the project root.",
                            node.path,
                            node.id,
                        )
                    )
                elif not node.retired and not target.is_file():
                    errors.append(
                        Diagnostic(
                            "SOURCE_MISSING",
                            f"Source does not exist: {source['path']}",
                            node.path,
                            node.id,
                            "warning",
                        )
                    )
    return Snapshot(root, files, nodes, errors, graph)


def load_snapshot(root: Path, *, ignore_state: bool = False) -> Snapshot:
    files, diagnostics = read_files(root)
    if not ignore_state:
        diagnostics.extend(runtime_diagnostics(root))
    return snapshot_from_files(root, files, diagnostics, check_sources=True)


def slugify(value: str) -> str:
    import re

    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-")[:80].rstrip("-")
    if not slug:
        raise SpecError([Diagnostic("SLUG", "Supply a summary containing letters or digits.")])
    return slug


def new_node(node_type: str, parents: list[str], body: str, slug: str) -> SpecNode:
    node_id = str(uuid.uuid4())
    return SpecNode(
        node_id,
        node_type,
        False,
        parents,
        body,
        f"{SPEC_DIR}/{node_id}--{slugify(slug)}.md",
        FORMAT_VERSION if node_type == "manifesto" else None,
    )


def safe_state(root: Path) -> Path:
    state = root / STATE_DIR
    if state.is_symlink() or (state.exists() and not state.is_dir()):
        raise SpecError([Diagnostic("STATE", "Runtime state must not be a symlink or file.")])
    state.mkdir(exist_ok=True)
    # Never follow a substituted lock, journal or staging file.
    if any(entry.is_symlink() for entry in state.iterdir()):
        raise SpecError([Diagnostic("STATE", "Symlinks are forbidden in runtime state.")])
    return state


@contextmanager
def workspace_lock(root: Path, *, recovering: bool = False):
    state = safe_state(root)
    if not recovering and ((state / "journal.json").exists() or any(state.glob("stage-*"))):
        raise SpecError([Diagnostic("RECOVERY", "Run specspec recover before another edit.")])
    lock = state / "lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise SpecError(
            [Diagnostic("LOCKED", "Workspace is locked; recover a stale lock explicitly.")]
        ) from error
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(str(os.getpid()))
        yield state
    finally:
        lock.unlink(missing_ok=True)


def encode(raw: bytes | None) -> str | None:
    return base64.b64encode(raw).decode("ascii") if raw is not None else None


def decode(raw: str | None) -> bytes | None:
    return base64.b64decode(raw, validate=True) if raw is not None else None


def write_journal(state: Path, data: dict[str, Any]) -> None:
    temp = state / "journal.tmp"
    temp.write_text(json.dumps(data), encoding="utf-8")
    os.replace(temp, state / "journal.json")


def cleanup(state: Path) -> None:
    for entry in state.glob("stage-*"):
        if entry.is_dir():
            shutil.rmtree(entry)
        else:
            entry.unlink()
    (state / "journal.json").unlink(missing_ok=True)
    (state / "journal.tmp").unlink(missing_ok=True)


def initialize(root: Path, body: str, slug: str = "project-manifesto") -> Snapshot:
    root = root.absolute()
    if not root.is_dir():
        raise SpecError([Diagnostic("WORKSPACE", "Project root must already exist.")], 2)
    destination = root / SPEC_DIR
    if destination.exists() or destination.is_symlink():
        raise SpecError(
            [Diagnostic("EXISTS", "Refusing to overwrite an existing _specspec workspace.")]
        )
    node = new_node("manifesto", [], body, slug)
    raw = serialize(node)
    candidate = snapshot_from_files(root, {node.path: raw})
    candidate.require_valid()
    with workspace_lock(root) as state:
        if state.stat().st_dev != root.stat().st_dev:
            raise SpecError(
                [Diagnostic("FILESYSTEM", "Staging and workspace must share a filesystem.")]
            )
        staging = state / "stage-init"
        staging.mkdir()
        (staging / Path(node.path).name).write_bytes(raw)
        write_journal(
            state, {"kind": "init", "files": {node.path: {"old": None, "new": encode(raw)}}}
        )
        if destination.exists() or destination.is_symlink():
            raise SpecError(
                [Diagnostic("CONCURRENT", "Workspace appeared while initialization was staged.")]
            )
        os.rename(staging, destination)
        result = load_snapshot(root, ignore_state=True)
        result.require_valid()
        cleanup(state)
    return result


def mutate(
    root: Path,
    operation: Callable[[Snapshot], dict[str, bytes]],
    *,
    expect: str | None = None,
    allow_legacy: bool = False,
) -> Snapshot:
    with workspace_lock(root) as state:
        before = load_snapshot(root, ignore_state=True)
        before.require_valid()
        if expect is not None and expect != before.fingerprint:
            raise SpecError(
                [Diagnostic("STALE", "Graph changed since it was displayed; refresh and retry.")]
            )
        if before.format_version != FORMAT_VERSION and not allow_legacy:
            raise SpecError(
                [
                    Diagnostic(
                        "MIGRATION", "Run specspec migrate --expect <fingerprint> before editing."
                    )
                ]
            )
        changes = operation(before)
        if not changes:
            return before
        proposed_files = {**before.files, **changes}
        candidate = snapshot_from_files(root, proposed_files, check_sources=True)
        candidate.require_valid()
        if state.stat().st_dev != (root / SPEC_DIR).stat().st_dev:
            raise SpecError(
                [Diagnostic("FILESYSTEM", "Staging and workspace must share a filesystem.")]
            )
        staged: dict[str, Path] = {}
        for index, (path, raw) in enumerate(sorted(changes.items())):
            temporary = state / f"stage-{index}"
            temporary.write_bytes(raw)
            staged[path] = temporary
        current_files, current_errors = read_files(root)
        if current_errors or current_files != before.files:
            cleanup(state)
            raise SpecError(
                [Diagnostic("CONCURRENT", "Files changed during the edit; refresh and retry.")]
            )
        write_journal(
            state,
            {
                "kind": "edit",
                "files": {
                    path: {"old": encode(before.files.get(path)), "new": encode(raw)}
                    for path, raw in changes.items()
                },
            },
        )
        for path, temporary in staged.items():
            if (root / SPEC_DIR).is_symlink():
                raise SpecError([Diagnostic("CONCURRENT", "Canonical directory became a symlink.")])
            target = root / path
            original = before.files.get(path)
            current = target.read_bytes() if target.exists() and not target.is_symlink() else None
            if target.is_symlink() or current != original:
                raise SpecError(
                    [
                        Diagnostic(
                            "CONCURRENT",
                            "File changed during replacement; recover before retrying.",
                            path,
                        )
                    ]
                )
            os.replace(temporary, target)
        result = load_snapshot(root, ignore_state=True)
        result.require_valid()
        cleanup(state)
    return result


def add_node(
    root: Path,
    node_type: str,
    parents: list[str],
    body: str,
    slug: str,
    expect: str | None = None,
    sources: list[dict[str, str]] | None = None,
) -> tuple[Snapshot, str]:
    node = new_node(node_type, parents, body, slug)
    node.sources = sources or []
    result = mutate(root, lambda _: {node.path: serialize(node)}, expect=expect)
    return result, node.id


def require_node(snapshot: Snapshot, node_id: str) -> SpecNode:
    graph = snapshot.require_valid()
    if node_id not in graph.nodes:
        raise SpecError([Diagnostic("NODE", f"Unknown node {node_id}.")])
    return graph.nodes[node_id]


def update_node(
    root: Path,
    node_id: str,
    *,
    body: str | None = None,
    parents: list[str] | None = None,
    sources: list[dict[str, str]] | None = None,
    expect: str | None = None,
) -> Snapshot:
    def operation(before: Snapshot) -> dict[str, bytes]:
        old = require_node(before, node_id)
        node = replace(
            old,
            body=old.body if body is None else body,
            parents=old.parents if parents is None else parents,
            sources=old.sources if sources is None else sources,
        )
        return {node.path: serialize(node, before.files[node.path])}

    return mutate(root, operation, expect=expect)


def set_retired(root: Path, ids: list[str], retired: bool, expect: str | None = None) -> Snapshot:
    def operation(before: Snapshot) -> dict[str, bytes]:
        changes: dict[str, bytes] = {}
        for node_id in ids:
            node = replace(require_node(before, node_id), retired=retired)
            changes[node.path] = serialize(node, before.files[node.path])
        return changes

    return mutate(root, operation, expect=expect)


def migrate(root: Path, expect: str | None = None) -> Snapshot:
    """Validate v1 integrity, then journal the entire approval-free conversion."""

    def operation(before: Snapshot) -> dict[str, bytes]:
        if before.format_version == FORMAT_VERSION:
            return {}
        return {
            node.path: serialize(
                replace(
                    node,
                    format_version=FORMAT_VERSION if node.type == "manifesto" else None,
                    legacy_status=None,
                ),
                before.files[node.path],
            )
            for node in before.nodes
        }

    return mutate(root, operation, expect=expect, allow_legacy=True)


def recover(root: Path, *, force_lock: bool = False) -> dict[str, Any]:
    state = safe_state(root)
    lock = state / "lock"
    if lock.exists():
        if not force_lock:
            raise SpecError(
                [
                    Diagnostic(
                        "LOCKED", "Confirm no writer is running, then use recover --force-lock."
                    )
                ]
            )
        lock.unlink()
    with workspace_lock(root, recovering=True):
        journal_path = state / "journal.json"
        if not journal_path.exists():
            cleanup(state)
            return {"restored": []}
        try:
            journal = json.loads(journal_path.read_text(encoding="utf-8"))
            if journal["kind"] not in {"edit", "init"} or not isinstance(journal["files"], dict):
                raise ValueError("Unsupported journal.")
            originals: dict[str, bytes | None] = {}
            for path, states in journal["files"].items():
                parts = PurePosixPath(path).parts
                if len(parts) != 2 or parts[0] != SPEC_DIR or "\\" in path:
                    raise ValueError("Unsafe journal path.")
                old, new = decode(states["old"]), decode(states["new"])
                target = root / path
                if (root / SPEC_DIR).is_symlink() or target.is_symlink():
                    raise ValueError("Canonical paths must not be symlinks.")
                current = target.read_bytes() if target.exists() else None
                if current not in (old, new):
                    raise ValueError(f"External edit to {path}; refusing to overwrite it.")
                originals[path] = old
            if journal["kind"] == "init":
                if any(original is not None for original in originals.values()):
                    raise ValueError("Initialization journal cannot contain original files.")
                directory = root / SPEC_DIR
                if directory.exists():
                    expected = {Path(path).name for path in originals}
                    if {entry.name for entry in directory.iterdir()} != expected:
                        raise ValueError(
                            "Unexpected initialization files; recovery changed nothing."
                        )
        except (ValueError, KeyError, TypeError) as error:
            raise SpecError([Diagnostic("RECOVERY", str(error))]) from error
        for index, (path, original) in enumerate(originals.items()):
            target = root / path
            if original is None:
                target.unlink(missing_ok=True)
            else:
                staging = state / f"stage-recovery-{index}"
                staging.write_bytes(original)
                os.replace(staging, target)
        if journal["kind"] == "init" and (root / SPEC_DIR).exists():
            (root / SPEC_DIR).rmdir()
        elif journal["kind"] == "edit":
            load_snapshot(root, ignore_state=True).require_valid()
        cleanup(state)
        return {"restored": sorted(originals)}


def byte_hash(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

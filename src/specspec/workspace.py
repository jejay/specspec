"""Filesystem snapshots and recoverable, tool-managed edits."""

from __future__ import annotations

import base64
import json
import os
import secrets
import shutil
import subprocess
from collections.abc import Callable, Collection
from contextlib import contextmanager
from dataclasses import dataclass, replace
from importlib.resources import files as package_files
from pathlib import Path, PurePosixPath
from typing import Any

from .format import parse_node, read_document, serialize
from .graph import Graph, build_graph
from .model import FORMAT_VERSION, Diagnostic, SpecError, SpecNode
from .node_text import logical_bytes

SPEC_DIR = ".specspec"
STATE_DIR = ".specspec/local"


@dataclass
class Snapshot:
    root: Path
    files: dict[str, bytes]
    nodes: list[SpecNode]
    diagnostics: list[Diagnostic]
    graph: Graph | None
    commit: str | None = None
    declared_version: int | None = None
    created_instructions: bool | None = None
    # Transient invocation outcomes; excluded from snapshots' protocol/canonical data.
    mutation_actions: dict[str, list[str]] | None = None

    @property
    def valid(self) -> bool:
        return not any(d.severity == "error" for d in self.diagnostics)

    @property
    def complete(self) -> bool:
        return (not self.files and self.valid) or (
            self.graph is not None
            and len(self.graph.nodes) == len(self.files)
            and not any(
                d.code in {"DIRECTORY", "ENTRY", "IO", "VERSION", "STATE", "LOCKED", "RECOVERY"}
                for d in self.diagnostics
            )
        )

    def require_current(self) -> None:
        """Author identifiable documents, not unsupported formats or unsafe filesystems."""
        hard = [
            d
            for d in self.diagnostics
            if d.code in {"DIRECTORY", "ENTRY", "IO", "VERSION", "STATE", "LOCKED", "RECOVERY"}
        ]
        if hard or self.format_version != FORMAT_VERSION:
            raise SpecError(
                hard
                or [
                    Diagnostic(
                        "ROOT", "Repair the current-format manifesto before managed editing."
                    )
                ]
            )

    def require_valid(self) -> Graph:
        if not self.valid or self.graph is None:
            raise SpecError(
                self.diagnostics or [Diagnostic("EMPTY", "No specification graph exists.")]
            )
        return self.graph

    @property
    def format_version(self) -> int | None:
        return (
            self.declared_version
            if self.declared_version is not None
            else next(
                (node.format_version for node in self.nodes if node.type == "manifesto"), None
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "format_version": self.format_version,
            "nodes": [
                node.to_dict()
                for node in sorted(
                    self.graph.nodes.values() if self.graph else [], key=lambda n: n.id
                )
            ],
            "edges": sorted(
                [p, n.id]
                for n in (self.graph.nodes.values() if self.graph else [])
                for p in n.parents
            ),
            "valid": self.valid,
            "complete": self.complete,
            "inventory": sorted(self.files),
            "unreadable_paths": sorted(
                set(self.files)
                - {n.path for n in (self.graph.nodes.values() if self.graph else [])}
            ),
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
        [Diagnostic("WORKSPACE", "No .specspec directory found; run specspec init.")], 2
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
        return files, [Diagnostic("DIRECTORY", ".specspec must be a real directory.", SPEC_DIR)]
    for entry in sorted(directory.iterdir()):
        path = f"{SPEC_DIR}/{entry.name}"
        if entry.name == "local" and entry.is_dir() and not entry.is_symlink():
            continue
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
    if type(version) is not int or version != FORMAT_VERSION:
        errors.append(
            Diagnostic(
                "VERSION",
                f"Manifesto must declare current format_version: {FORMAT_VERSION}.",
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
            key = node.id.casefold()
            if key in seen:
                errors.append(
                    Diagnostic(
                        "DUPLICATE",
                        f"Duplicate or case-only ID also present in {seen[key]}.",
                        path,
                        node.id,
                    )
                )
                duplicates = True
            seen[key] = path
            nodes.append(node)
        except SpecError as error:
            errors.extend(error.diagnostics)
    graph = None
    ambiguous = (
        {
            n.id.casefold()
            for n in nodes
            if sum(other.id.casefold() == n.id.casefold() for other in nodes) > 1
        }
        if duplicates
        else set()
    )
    identified = [n for n in nodes if n.id.casefold() not in ambiguous]
    graph, graph_errors = build_graph(identified)
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
                elif "blob" not in source and not target.is_file():
                    errors.append(
                        Diagnostic(
                            "SOURCE_MISSING",
                            f"Source does not exist: {source['path']}",
                            node.path,
                            node.id,
                            "warning",
                        )
                    )
    return Snapshot(root, files, nodes, errors, graph, declared_version=version)


def load_snapshot(root: Path, *, ignore_state: bool = False) -> Snapshot:
    files, diagnostics = read_files(root)
    if not ignore_state:
        diagnostics.extend(runtime_diagnostics(root))
    return snapshot_from_files(root, files, diagnostics, check_sources=True)


def new_node(
    node_type: str,
    parents: list[str],
    body: str,
    *,
    reserved_ids: Collection[str] = (),
) -> SpecNode:
    reserved = {node_id.casefold() for node_id in reserved_ids}
    while True:
        node_id = base64.urlsafe_b64encode(secrets.token_bytes(5)).decode("ascii")
        if node_id.casefold() not in reserved:
            break
    return SpecNode(
        node_id,
        node_type,
        parents,
        body,
        f"{SPEC_DIR}/{node_id}.md",
        FORMAT_VERSION if node_type == "manifesto" else None,
    )


def safe_state(root: Path) -> Path:
    directory = root / SPEC_DIR
    if directory.is_symlink() or (directory.exists() and not directory.is_dir()):
        raise SpecError([Diagnostic("STATE", "Specification storage must be a real directory.")])
    directory.mkdir(exist_ok=True)
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


def initialization_available(root: Path) -> bool:
    """Only absence or a safe empty/local-only directory is an initialization target."""
    directory = root / SPEC_DIR
    if directory.is_symlink():
        return False
    if not directory.exists():
        return True
    return directory.is_dir() and all(entry.name == "local" for entry in directory.iterdir())


def initialize(root: Path, body: str) -> Snapshot:
    root = root.absolute()
    if not root.is_dir():
        raise SpecError([Diagnostic("WORKSPACE", "Project root must already exist.")], 2)
    if not initialization_available(root):
        raise SpecError(
            [Diagnostic("EXISTS", "Refusing to overwrite an existing .specspec workspace.")]
        )
    # Validate payloads without allocating an identity outside the writer lock.
    example = SpecNode("AAAAAAA=", "manifesto", [], body, f"{SPEC_DIR}/AAAAAAA=.md", FORMAT_VERSION)
    snapshot_from_files(root, {example.path: serialize(example)}).require_valid()
    if diagnostics := runtime_diagnostics(root):
        raise SpecError(diagnostics)
    instructions = root / "AGENTS.md"
    if instructions.is_symlink() or (instructions.exists() and not instructions.is_file()):
        raise SpecError([Diagnostic("INSTRUCTIONS", "AGENTS.md must be a regular file or absent.")])
    old_guide = None
    if instructions.exists():
        with instructions.open("rb") as stream:
            old_guide = stream.read(16 * 1024 * 1024 + 1)
        if len(old_guide) > 16 * 1024 * 1024:
            raise SpecError(
                [Diagnostic("INSTRUCTIONS", "AGENTS.md exceeds the 16 MiB append limit.")]
            )
    template = package_files("specspec").joinpath("templates/AGENTS.md").read_bytes()
    separator = (
        b""
        if not old_guide or old_guide.endswith(b"\n\n")
        else b"\n"
        if old_guide.endswith((b"\n", b"\r"))
        else b"\n\n"
    )
    guide = (old_guide or b"") + separator + template
    # Explicit init authorizes Git initialization, not identity, hooks or index edits.
    environment = {
        key: value
        for key, value in os.environ.items()
        if key
        not in {
            "GIT_DIR",
            "GIT_WORK_TREE",
            "GIT_COMMON_DIR",
            "GIT_INDEX_FILE",
            "GIT_OBJECT_DIRECTORY",
            "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        }
    }
    if len(environment) != len(os.environ):
        raise SpecError(
            [
                Diagnostic(
                    "GIT", "Unset Git directory/index overrides before initializing this project."
                )
            ],
            2,
        )
    try:
        git = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            env=environment,
            timeout=30,
        )
        if git.returncode or git.stdout.strip() != b"true":
            git = subprocess.run(
                ["git", "-C", str(root), "init", "--quiet"],
                capture_output=True,
                env=environment,
                timeout=30,
            )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise SpecError(
            [Diagnostic("GIT", f"Git is required for initialization: {error}")], 2
        ) from error
    if git.returncode:
        raise SpecError(
            [
                Diagnostic(
                    "GIT", git.stderr.decode("utf8", errors="replace").strip() or "git init failed."
                )
            ],
            2,
        )
    # Reuse checkout-local exclusion protection without writing project ignore rules.
    from .annotations import ensure_ignored

    ensure_ignored(root)
    with workspace_lock(root) as state:
        if not initialization_available(root):
            raise SpecError([Diagnostic("CONCURRENT", "Workspace appeared during initialization.")])
        if state.stat().st_dev != root.stat().st_dev:
            raise SpecError(
                [Diagnostic("FILESYSTEM", "Staging and workspace must share a filesystem.")]
            )
        node = new_node("manifesto", [], body)
        raw = serialize(node)
        snapshot_from_files(root, {node.path: raw}).require_valid()
        staged_node, staged_guide = state / "stage-init", state / "stage-init-agents"
        staged_node.write_bytes(raw)
        staged_guide.write_bytes(guide)
        write_journal(
            state,
            {
                "kind": "init",
                "files": {
                    node.path: {"old": None, "new": encode(raw)},
                    "AGENTS.md": {"old": encode(old_guide), "new": encode(guide)},
                },
            },
        )
        if (root / SPEC_DIR).is_symlink():
            raise SpecError(
                [
                    Diagnostic(
                        "CONCURRENT",
                        "Specification storage became a symlink; recover before retrying.",
                    )
                ]
            )
        os.link(staged_node, root / node.path)
        current = (
            instructions.read_bytes()
            if instructions.exists() and not instructions.is_symlink()
            else None
        )
        if instructions.is_symlink() or current != old_guide:
            raise SpecError(
                [
                    Diagnostic(
                        "CONCURRENT", "Instructions changed during init; recover before retrying."
                    )
                ]
            )
        if old_guide is None:
            os.link(staged_guide, instructions)
        else:
            os.replace(staged_guide, instructions)
        result = load_snapshot(root, ignore_state=True)
        if (
            result.files != {node.path: raw}
            or instructions.is_symlink()
            or instructions.read_bytes() != guide
        ):
            raise SpecError(
                [Diagnostic("CONCURRENT", "Files changed during init; recover before retrying.")]
            )
        result.require_valid()
        result.created_instructions = old_guide is None
        result.mutation_actions = {"added": [node.id]}
        cleanup(state)
    return result


def mutate(
    root: Path,
    operation: Callable[[Snapshot], dict[str, bytes | None]],
    *,
    require_valid: bool = False,
    dry_run: bool = False,
) -> Snapshot:
    with workspace_lock(root) as state:
        before = load_snapshot(root, ignore_state=True)
        before.require_current()
        changes = operation(before)
        if not changes:
            if require_valid:
                before.require_valid()
            before.mutation_actions = {}
            return before
        for path, raw in changes.items():
            pure = PurePosixPath(path)
            if (
                len(pure.parts) != 2
                or pure.parent.as_posix() != SPEC_DIR
                or "\\" in path
                or pure.as_posix() != path
            ):
                raise SpecError(
                    [Diagnostic("PATH", "Mutations require direct canonical node paths.")]
                )
            if raw is not None:
                data, body = read_document(raw, path)
                node = parse_node(data, body, path)
                if node.type == "manifesto" and node.parents:
                    raise SpecError([Diagnostic("PARENTS", "The manifesto cannot be reparented.")])
            elif any(n.path == path and n.type == "manifesto" for n in before.nodes):
                raise SpecError([Diagnostic("DELETE", "The manifesto cannot be deleted.")])
        proposed_files = {
            path: raw for path, raw in {**before.files, **changes}.items() if raw is not None
        }
        candidate = snapshot_from_files(root, proposed_files, check_sources=True)
        candidate.require_current()
        for path, raw in changes.items():
            if raw is not None:
                require_node(candidate, PurePosixPath(path).stem)
        if require_valid:
            candidate.require_valid()
        actions: dict[str, list[str]] = {}
        for path, raw in changes.items():
            original = before.files.get(path)
            if logical_bytes(raw) == logical_bytes(original):
                action = "unchanged"
            elif original is None:
                action = "added"
            elif raw is None:
                action = "deleted"
            else:
                action = "modified"
            actions.setdefault(action, []).append(PurePosixPath(path).stem)
        candidate.mutation_actions = actions
        if dry_run:
            return candidate
        if state.stat().st_dev != (root / SPEC_DIR).stat().st_dev:
            raise SpecError(
                [Diagnostic("FILESYSTEM", "Staging and workspace must share a filesystem.")]
            )
        staged: dict[str, Path] = {}
        for index, (path, raw) in enumerate(sorted(changes.items())):
            if raw is not None:
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
        for path, raw in sorted(changes.items()):
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
            if raw is None:
                target.unlink()
            else:
                os.replace(staged[path], target)
        result = load_snapshot(root, ignore_state=True)
        if result.files != candidate.files:
            raise SpecError(
                [
                    Diagnostic(
                        "CONCURRENT", "Files changed after replacement; recover before retrying."
                    )
                ]
            )
        result.mutation_actions = actions
        cleanup(state)
    return result


def add_node(
    root: Path,
    node_type: str,
    parents: list[str],
    body: str,
    sources: list[dict[str, Any]] | None = None,
    *,
    require_valid: bool = False,
) -> tuple[Snapshot, str]:
    node_id = ""

    def operation(before: Snapshot) -> dict[str, bytes]:
        nonlocal node_id
        reserved = (
            {n.id for n in before.nodes}
            | {PurePosixPath(path).stem for path in before.files}
            | {p for n in before.nodes for p in n.parents}
        )
        node = new_node(node_type, parents, body, reserved_ids=reserved)
        node.sources = sources or []
        node_id = node.id
        return {node.path: serialize(node)}

    result = mutate(root, operation, require_valid=require_valid)
    return result, node_id


def require_node(snapshot: Snapshot, node_id: str) -> SpecNode:
    matches = [n for n in snapshot.nodes if n.id.casefold() == node_id.casefold()]
    if len(matches) > 1:
        raise SpecError(
            [Diagnostic("DUPLICATE", f"Ambiguous node {node_id}; repair its identity first.")]
        )
    if not matches or matches[0].id != node_id:
        raise SpecError([Diagnostic("NODE", f"Unknown node {node_id}, or its file is unreadable.")])
    return matches[0]


def update_node(
    root: Path,
    node_id: str,
    *,
    body: str | None = None,
    parents: list[str] | None = None,
    sources: list[dict[str, Any]] | None = None,
    require_valid: bool = False,
) -> Snapshot:
    def operation(before: Snapshot) -> dict[str, bytes]:
        old = require_node(before, node_id)
        if old.type == "manifesto" and parents:
            raise SpecError([Diagnostic("PARENTS", "The manifesto cannot be reparented.")])
        node = replace(
            old,
            body=old.body if body is None else body,
            parents=old.parents if parents is None else parents,
            sources=old.sources if sources is None else sources,
        )
        return {node.path: serialize(node, before.files[node.path])}

    return mutate(root, operation, require_valid=require_valid)


def delete_nodes(
    root: Path,
    ids: list[str],
    *,
    allow_uncommitted: bool = False,
    confirm: Callable[[dict[str, Any]], bool] | None = None,
    reviewed_plan: dict[str, Any] | None = None,
    require_valid: bool = False,
) -> Snapshot:
    """Delete exactly the requested files in one recoverable, warned transaction."""
    # Local import avoids the Git/snapshot module cycle; plans never perform writes.
    from .deletion import deletion_plan, deletion_warnings

    warnings: list[Diagnostic] = []

    def operation(before: Snapshot) -> dict[str, bytes | None]:
        nonlocal warnings
        plan = deletion_plan(before, ids)
        warnings = deletion_warnings(plan)
        if reviewed_plan is not None and reviewed_plan != plan:
            raise SpecError(
                [
                    Diagnostic(
                        "DELETE_PLAN_CHANGED",
                        "Deletion scope or uncommitted warnings changed; "
                        "preview and confirm again.",
                    )
                ]
            )
        if confirm is not None:
            if not confirm(plan):
                raise SpecError(
                    [Diagnostic("DELETE_CANCELLED", "Deletion cancelled; no files removed.")]
                )
        elif warnings and not allow_uncommitted:
            raise SpecError(
                [
                    *warnings,
                    Diagnostic(
                        "DELETE_CONFIRMATION",
                        "Confirm the full deletion plan or explicitly allow uncommitted deletion.",
                    ),
                ]
            )
        return {node["path"]: None for node in plan["nodes"]}

    result = mutate(root, operation, require_valid=require_valid)
    result.diagnostics.extend(warnings)
    return result


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
                pure = PurePosixPath(path)
                node_path = (
                    len(pure.parts) == 2
                    and pure.parent.as_posix() == SPEC_DIR
                    and pure.as_posix() == path
                    and "\\" not in path
                )
                instruction_path = journal["kind"] == "init" and path == "AGENTS.md"
                if not (node_path or instruction_path):
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
                if any(
                    original is not None
                    for path, original in originals.items()
                    if path != "AGENTS.md"
                ):
                    raise ValueError("Initialization journal cannot contain original nodes.")
                directory = root / SPEC_DIR
                if directory.exists():
                    expected = {
                        Path(path).name for path in originals if path.startswith(SPEC_DIR + "/")
                    }
                    if (
                        not {entry.name for entry in directory.iterdir() if entry.name != "local"}
                        <= expected
                    ):
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
        diagnostics = (
            load_snapshot(root, ignore_state=True).diagnostics if journal["kind"] == "edit" else []
        )
        cleanup(state)
        return {
            "restored": sorted(originals),
            "graph_valid": not any(d.severity == "error" for d in diagnostics),
            "diagnostics": [d.to_dict() for d in diagnostics],
        }

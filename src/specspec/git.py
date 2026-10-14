"""Git snapshots, semantic graph diffs, and index-validation hooks."""

from __future__ import annotations

import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

from .git_objects import read_blobs
from .model import Diagnostic, SpecError
from .workspace import SPEC_DIR, Snapshot, snapshot_from_files


def run_git(root: Path, *args: str) -> bytes:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            check=False,
            env={
                **os.environ,
                "GIT_NO_LAZY_FETCH": "1",
                "GIT_OPTIONAL_LOCKS": "0",
                "GIT_ALLOW_PROTOCOL": "",
            },
        )
    except OSError as error:
        raise SpecError([Diagnostic("GIT", str(error))], 2) from error
    if completed.returncode:
        raise SpecError(
            [Diagnostic("GIT", completed.stderr.decode("utf-8", errors="replace").strip())], 2
        )
    return completed.stdout


def repository_paths(root: Path) -> tuple[Path, str]:
    repository = Path(run_git(root, "rev-parse", "--show-toplevel").decode().strip()).resolve()
    relative = root.resolve().relative_to(repository).as_posix()
    prefix = SPEC_DIR if relative == "." else f"{relative}/{SPEC_DIR}"
    return repository, prefix


def resolve_commit(root: Path, ref: str) -> str:
    return (
        run_git(root, "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}")
        .decode()
        .strip()
    )


def unborn_head(root: Path) -> bool:
    """Only an unresolved symbolic HEAD is an empty baseline, not a bad user ref."""
    try:
        branch = run_git(root, "symbolic-ref", "--quiet", "HEAD").decode().strip()
    except SpecError:
        return False
    completed = subprocess.run(
        ["git", "-C", str(root), "show-ref", "--verify", "--quiet", branch],
        capture_output=True,
    )
    return completed.returncode == 1


def git_snapshot(
    root: Path,
    ref: str | None = None,
    *,
    staged: bool = False,
    allow_empty: bool = False,
    cache: dict | None = None,
) -> Snapshot:
    repository, prefix = repository_paths(root)
    files: dict[str, bytes] = {}
    diagnostics: list[Diagnostic] = []
    if staged:
        records = run_git(
            repository, "--literal-pathspecs", "ls-files", "--stage", "-z", "--", prefix
        ).split(b"\0")
    else:
        # Resolve refs first; never pass user input as an option to ls-tree.
        if allow_empty and ref == "HEAD" and unborn_head(repository):
            return snapshot_from_files(root, {}, allow_empty=True)
        commit = resolve_commit(repository, str(ref))
        records = run_git(
            repository, "--literal-pathspecs", "ls-tree", "-r", "-z", commit, "--", prefix
        ).split(b"\0")
    entries: list[tuple[str, str]] = []
    for record in records:
        if not record:
            continue
        metadata, encoded_path = record.split(b"\t", 1)
        mode, second, third = metadata.decode().split()
        name = encoded_path.decode("utf-8", errors="surrogateescape")
        path = SPEC_DIR + name[len(prefix) :]
        object_id = second if staged else third
        if staged and third != "0":
            diagnostics.append(
                Diagnostic("CONFLICT", "Resolve staged merge conflicts before committing.", path)
            )
            continue
        if mode not in {"100644", "100755"}:
            diagnostics.append(
                Diagnostic("ENTRY", "Git entry must be a regular Markdown node.", path)
            )
            continue
        if not path.endswith(".md") or len(Path(path).parts) != 2:
            diagnostics.append(Diagnostic("ENTRY", "Only direct Markdown nodes are allowed.", path))
            continue
        entries.append((path, object_id))
    hints = {}
    if not staged and cache and cache.get("commit") == commit:
        for path, oid in entries:
            value = cache.get("files", {}).get(path)
            if isinstance(value, str):
                hints[oid] = value.encode("utf-8")
    blobs, failures = read_blobs(repository, [oid for _, oid in entries], hints)
    for path, oid in entries:
        if oid in failures:
            code = "FORMAT" if "1 MiB" in failures[oid] else "GIT"
            diagnostics.append(Diagnostic(code, failures[oid], path))
        else:
            files[path] = blobs[oid]
    result = snapshot_from_files(root, files, diagnostics, allow_empty=allow_empty)
    if not staged:
        result.commit = commit
    return result


def semantic_diff(base: Snapshot, target: Snapshot) -> dict[str, Any]:
    old_nodes = {node.id: node for node in base.nodes}
    new_nodes = {node.id: node for node in target.nodes}
    changes = []
    affected: set[str] = set()
    for node_id in sorted(old_nodes.keys() | new_nodes.keys()):
        old, new = old_nodes.get(node_id), new_nodes.get(node_id)
        if old is None:
            kind, fields = "added", []
        elif new is None:
            kind, fields = "removed", []
        else:
            old_semantic, new_semantic = old.semantic(), new.semantic()
            fields = sorted(
                key
                for key in old_semantic.keys() | new_semantic.keys()
                if old_semantic.get(key) != new_semantic.get(key)
            )
            if old.path != new.path:
                fields.append("path")
            if not fields:
                continue
            kind = "renamed" if fields == ["path"] else "changed"
        changes.append({"id": node_id, "kind": kind, "fields": fields})
        if kind != "renamed":
            affected.add(node_id)
            for snapshot in (base, target):
                if snapshot.graph and node_id in snapshot.graph.nodes:
                    affected.update(snapshot.graph.closure(node_id))
    old_edges = {tuple(edge) for edge in base.graph.edges()} if base.graph else set()
    new_edges = {tuple(edge) for edge in target.graph.edges()} if target.graph else set()
    file_changes = [
        {
            "path": path,
            "kind": "added"
            if path not in base.files
            else "removed"
            if path not in target.files
            else "changed",
        }
        for path in sorted(base.files.keys() | target.files.keys())
        if base.files.get(path) != target.files.get(path)
        or (path in base.files) != (path in target.files)
    ]
    return {
        "base": base.to_dict(),
        "target": target.to_dict(),
        "changes": changes,
        "added_edges": sorted(map(list, new_edges - old_edges)),
        "removed_edges": sorted(map(list, old_edges - new_edges)),
        "affected": sorted(affected),
        "file_changes": file_changes,
        "impact_complete": base.valid and target.valid,
    }


def source_change_impact(
    root: Path, base_ref: str, target_ref: str | None, base: Snapshot, target: Snapshot
) -> dict[str, Any]:
    references = {
        source["path"]
        for snapshot in (base, target)
        for node in snapshot.nodes
        for source in node.sources
    }
    if not references:
        return {"source_changes": [], "source_affected": []}
    repository, prefix = repository_paths(root)
    project_prefix = prefix.removesuffix(SPEC_DIR)
    full_paths = [project_prefix + path for path in sorted(references)]
    empty_head = base_ref == "HEAD" and unborn_head(repository)
    commits = [] if empty_head else [resolve_commit(repository, base_ref)]
    if target_ref is not None:
        commits.append(resolve_commit(repository, target_ref))
    changed = (
        [path.encode("utf-8") for path in full_paths]
        if empty_head
        else run_git(
            repository,
            "--literal-pathspecs",
            "diff",
            "--name-only",
            "-z",
            "--no-renames",
            *commits,
            "--",
            *full_paths,
        ).split(b"\0")
    )
    if target_ref is None:
        # git diff excludes untracked files, including new referenced realizations.
        changed.extend(
            run_git(
                repository,
                "--literal-pathspecs",
                "ls-files",
                "--others",
                "--exclude-standard",
                "-z",
                "--",
                *full_paths,
            ).split(b"\0")
        )
    changed_paths = {
        name.decode("utf-8", errors="surrogateescape")[len(project_prefix) :]
        for name in changed
        if name
    } & references
    affected: set[str] = set()
    changes: list[dict[str, Any]] = []
    for path in sorted(changed_paths):
        implementation_ids: set[str] = set()
        for snapshot in (base, target):
            for node in snapshot.nodes:
                if any(source["path"] == path for source in node.sources):
                    implementation_ids.add(node.id)
                    affected.add(node.id)
                    if snapshot.graph:
                        affected.update(snapshot.graph.closure(node.id, ancestors=True))
        changes.append({"path": path, "implementation_ids": sorted(implementation_ids)})
    return {"source_changes": changes, "source_affected": sorted(affected)}


def install_hook(root: Path) -> Path:
    resolved = (
        run_git(root, "rev-parse", "--path-format=absolute", "--git-path", "hooks/pre-commit")
        .decode()
        .strip()
    )
    path = Path(resolved)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation avoids overwriting existing hooks, including a racing installer.
    command = " ".join(
        shlex.quote(arg)
        for arg in [
            sys.executable.replace("\\", "/"),
            "-m",
            "specspec",
            "--root",
            str(root.resolve()).replace("\\", "/"),
            "hook",
            "check",
        ]
    )
    script = (
        "#!/bin/sh\n# Installed by SpecSpec; validates staged nodes, not working files.\n"
        f"exec {command}\n"
    )
    try:
        with path.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(script)
    except FileExistsError as error:
        raise SpecError(
            [
                Diagnostic(
                    "HOOK_EXISTS",
                    "Existing hook preserved; chain specspec hook check manually.",
                    str(path),
                )
            ]
        ) from error
    os.chmod(path, path.stat().st_mode | 0o111)
    return path

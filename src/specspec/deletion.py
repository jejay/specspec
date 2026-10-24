"""Exact-file deletion plans, retained dependency findings and Git warnings."""

from __future__ import annotations

from typing import Any

from .git import repository_paths, run_git
from .inspection import findings, walks
from .model import Diagnostic, SpecError
from .workspace import SPEC_DIR, Snapshot, require_node, snapshot_from_files


def deletion_plan(snapshot: Snapshot, ids: list[str]) -> dict[str, Any]:
    """Select only named files; diagnose the retained declarations without repairing."""
    if not ids or any(not isinstance(key, str) for key in ids) or len(ids) != len(set(ids)):
        raise SpecError([Diagnostic("DELETE", "Name a nonempty batch of distinct node IDs.")], 2)
    snapshot.require_current()
    nodes = [require_node(snapshot, key) for key in ids]
    if any(node.type == "manifesto" for node in nodes):
        raise SpecError([Diagnostic("DELETE", "The manifesto cannot be deleted.")])
    selected = set(ids)
    paths = {node.path: node.id for node in sorted(nodes, key=lambda n: n.id)}
    remaining = snapshot_from_files(
        snapshot.root,
        {path: raw for path, raw in snapshot.files.items() if path not in paths},
        check_sources=True,
    )
    consequences = findings(remaining)
    potential = walks(snapshot.graph, selected) - selected
    statuses: dict[str, str] = {}
    available, note = True, ""
    try:
        repository, prefix = repository_paths(snapshot.root)
        # status accounts for clean filters/CRLF, staged changes and untracked/ignored
        # files. Disable optional index refresh/cache writes and executable fsmonitor.
        output = run_git(
            repository,
            "--no-optional-locks",
            "--literal-pathspecs",
            "-c",
            "core.fsmonitor=false",
            "status",
            "--porcelain=v1",
            "-z",
            "--untracked-files=all",
            "--ignored=traditional",
            "--",
            prefix,
        )
        records = iter(output.split(b"\0"))
        for record in records:
            if not record:
                continue
            status = record[:2].decode("ascii")
            name = record[3:].decode("utf-8", errors="surrogateescape")
            if "R" in status or "C" in status:
                # With -z the destination is first, followed by the original path.
                next(records)
            if name.startswith(prefix + "/"):
                path = SPEC_DIR + name[len(prefix) :]
                if path in paths:
                    statuses[path] = status
    except SpecError as error:
        available, note = False, f"Git assessment unavailable: {error}"
        statuses = dict.fromkeys(paths, "unknown")
    return {
        "requested_ids": sorted(ids),
        "deleted_ids": sorted(selected),
        "nodes": [{"id": key, "path": path} for path, key in paths.items()],
        "uncommitted": [
            {"id": key, "path": path, "status": statuses[path]}
            for path, key in paths.items()
            if path in statuses
        ],
        "git_available": available,
        "git_note": note,
        **consequences,
        "potentially_affected": sorted(potential),
    }


def deletion_warnings(plan: dict[str, Any]) -> list[Diagnostic]:
    return [
        Diagnostic(
            "DELETE_UNCOMMITTED" if plan["git_available"] else "DELETE_GIT_UNAVAILABLE",
            (
                f"Node {node['id']} has uncommitted Git changes ({node['status']}); "
                "deletion will remove its current file. Staging is not committing."
                if plan["git_available"]
                else f"Cannot establish that node {node['id']} is committed. {plan['git_note']}"
            ),
            node["path"],
            node["id"],
            "warning",
        )
        for node in plan["uncommitted"]
    ]

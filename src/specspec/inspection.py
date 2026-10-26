"""Non-writing broken-justification evidence; structural scope is not owner intent."""

from __future__ import annotations

from collections import deque
from pathlib import PurePosixPath

from .model import Diagnostic, SpecError
from .node_text import logical_bytes


def findings(snapshot):
    graph = snapshot.graph
    known = graph.nodes if graph else {}
    references = []
    for node in sorted(known.values(), key=lambda n: n.id):
        for parent in sorted(node.parents):
            if parent not in known:
                path = f".specspec/{parent}.md"
                reason = "unreadable" if path in snapshot.files else "missing"
                if any(n.id.casefold() == parent.casefold() for n in snapshot.nodes):
                    reason = (
                        "ambiguous"
                        if sum(n.id.casefold() == parent.casefold() for n in snapshot.nodes) > 1
                        else "case-mismatch"
                    )
                references.append(
                    {"child": node.id, "parent": parent, "path": path, "reason": reason}
                )
    seeds = {
        d.node_id
        for d in snapshot.diagnostics
        if d.severity == "error" and d.node_id in known and not d.code.startswith("SOURCE")
    }
    seeds.update(r["child"] for r in references)
    affected = walks(graph, seeds) if graph else set(seeds)
    return {
        "graph_valid": snapshot.valid,
        "analysis_complete": snapshot.complete,
        "broken_references": references,
        "issue_ids": sorted(seeds),
        "potentially_affected": sorted(affected),
        "unreadable_paths": sorted(set(snapshot.files) - {n.path for n in known.values()}),
    }


def walks(graph, starts, *, ancestors=False):
    """Known-node reachability, also seeded by declared missing parent identities."""
    if graph is None:
        return set()
    adjacency = graph.parents if ancestors else graph.children
    seen, pending = set(), list(starts)
    if not ancestors:
        for node in graph.nodes.values():
            if set(node.parents).intersection(starts):
                pending.append(node.id)
    while pending:
        current = pending.pop()
        if current in seen:
            continue
        seen.add(current)
        pending.extend(adjacency.get(current, ()))
    return seen


def witnesses(snapshot, causes, selected):
    """One finite shortest deterministic witness per cause/member, not path unfolding."""
    graph = snapshot.graph
    if not graph:
        return []
    result = []
    for cause in sorted(causes):
        previous = {cause: None}
        queue = deque([cause])
        missing_children = sorted(n.id for n in graph.nodes.values() if cause in n.parents)
        while queue:
            current = queue.popleft()
            for child in (
                sorted(graph.children[current]) if current in graph.nodes else missing_children
            ):
                if child not in previous:
                    previous[child] = current
                    queue.append(child)
        for id in sorted(selected & previous.keys() - {cause}):
            path, current = [], id
            while current is not None:
                path.append(current)
                current = previous[current]
            result.append({"cause": cause, "node_id": id, "path": list(reversed(path))})
    return result


def repair_context(base, target, changes, node_ids=()):
    """Deduplicated old/current bindings and explicit cause evidence, never a verdict."""
    old, new = (dict(s.graph.nodes) if s.graph else {} for s in (base, target))
    issues = findings(target)
    seeds = (
        {c["id"] for c in changes}
        | set(issues["issue_ids"])
        | {r["parent"] for r in issues["broken_references"]}
    )
    # Literal-only edits are evidence too.
    for id, node in (old | new).items():
        if logical_bytes(base.files.get(node.path)) != logical_bytes(target.files.get(node.path)):
            seeds.add(id)
    available = set(old) | set(new) | {p for n in [*old.values(), *new.values()] for p in n.parents}
    if node_ids:
        unknown = set(node_ids) - available
        if unknown:
            raise SpecError(
                [Diagnostic("NODE", "Unknown context IDs: " + ", ".join(sorted(unknown)))]
            )
        seeds = set(node_ids)
    affected = walks(base.graph, seeds) | walks(target.graph, seeds)
    selected = (affected | seeds) & available
    selected |= walks(base.graph, selected, ancestors=True) | walks(
        target.graph, selected, ancestors=True
    )
    records = []
    for id in sorted(selected & (old.keys() | new.keys())):
        a, b = old.get(id), new.get(id)
        record = {
            "id": id,
            "current": b.to_dict() if b else None,
            "unchanged": bool(a and b and a.to_dict() == b.to_dict()),
        }
        if not record["unchanged"]:
            record["before"] = a.to_dict() if a else None
        if b:
            record["surviving_parents"] = sorted(p for p in b.parents if p in new)
        records.append(record)
    unknown = sorted(selected - old.keys() - new.keys())
    return {
        "scope": sorted(seeds),
        "observed_changes": changes,
        "findings": issues,
        "potentially_affected": sorted(affected),
        "records": records,
        "unavailable_ids": unknown,
        "unreadable_paths": {
            "base": base.to_dict()["unreadable_paths"],
            "target": target.to_dict()["unreadable_paths"],
        },
        "cause_paths": [
            {"basis": side, **row}
            for side, snapshot in [("base", base), ("target", target)]
            for row in witnesses(snapshot, seeds, selected)
        ],
        "complete": base.complete and target.complete,
        "interpretation": (
            "Observed edits and potential dependency scope are evidence, "
            "not a determination of owner intent or semantic justification."
        ),
    }


def raw_document(snapshot, node_id=None, path=None):
    if path is None:
        path = f".specspec/{node_id}.md"
    pure = PurePosixPath(path)
    if (
        len(pure.parts) != 2
        or pure.parent.as_posix() != ".specspec"
        or "\\" in path
        or pure.suffix != ".md"
        or pure.as_posix() != path
    ):
        raise SpecError([Diagnostic("PATH", "Raw reads require a direct .specspec/*.md path.")], 2)
    if path not in snapshot.files:
        raise SpecError([Diagnostic("NODE", "No readable canonical file at " + path)])
    try:
        return {"path": path, "text": snapshot.files[path].decode("utf8")}
    except UnicodeError:
        import base64

        return {
            "path": path,
            "bytes_base64": base64.b64encode(snapshot.files[path]).decode("ascii"),
            "note": "Non-UTF-8 bytes; no normalized text available.",
        }

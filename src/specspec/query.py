"""Plain current-state DAG reads with sparse revision and source-change hints."""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from .annotations import snapshots
from .git import repository_paths, semantic_diff, source_change_impact
from .graph import Graph
from .model import Diagnostic, SpecError
from .output import json_text
from .query_select import Limit, reachable, scope_result, select_graph
from .query_sources import contract_state, source_comparisons, source_contract_impact
from .sources import BAD_OUTCOMES
from .workspace import Snapshot

STATUS = {"added": "added", "changed": "modified", "removed": "deleted"}


@dataclass
class QueryComparison:
    base: Snapshot
    target: Snapshot
    result: dict
    display: Graph | None = None

    @property
    def diagnostics(self):
        return self.base.diagnostics + self.target.diagnostics


def compare_snapshots(base: Snapshot, target: Snapshot) -> QueryComparison:
    if base.files or not base.valid:
        base.require_valid()
    target.require_valid()
    result = semantic_diff(base, target)
    result.update(
        base_ref=base.commit or "HEAD",
        target_ref=target.commit or "workspace",
        base_commit=base.commit,
        target_commit=target.commit,
        source_changes=[],
        source_affected=[],
        source_resolutions=[],
        source_contract_affected=[],
        source_contract_complete=False,
        source_impact_complete=False,
        notes=[],
    )
    return QueryComparison(base, target, result)


def read_query(
    root: Path,
    base=None,
    target=None,
    *,
    node_id=None,
    min_distance=None,
    max_distance=None,
    influence=None,
    with_ancestors: bool = False,
) -> QueryComparison:
    limits = {
        name: Limit.parse(value, name)
        for name, value in (
            ("min-distance", min_distance),
            ("max-distance", max_distance),
            ("influence", influence),
        )
        if value is not None
    }
    for ref in (base, target):
        if ref is not None and (not ref or len(ref) > 1024):
            raise SpecError(
                [Diagnostic("QUERY", "Supply a nonempty revision of at most 1024 characters.")], 2
            )
    old, new = snapshots(root, base or "HEAD", target or "workspace")
    comparison = compare_snapshots(old, new)
    result = comparison.result
    result.update(base_ref=base or "HEAD", target_ref=target or "workspace")
    source_ids = None
    if node_id is not None or limits:
        start = (
            node_id
            if node_id is not None
            else next(n.id for n in new.nodes if n.type == "manifesto")
        )
        comparison.display, result["selection"] = select_graph(
            comparison_graph(old, new), start, limits, with_ancestors=with_ancestors
        )
        included = set(comparison.display.nodes)
        source_ids = set()
        for snapshot in (old, new):
            if snapshot.graph:
                source_ids.update(
                    i
                    for i in reachable(snapshot.graph, included)
                    if snapshot.graph.nodes[i].sources
                )
        result["selection"]["source_evidence_ids"] = sorted(source_ids)
    try:
        repository_paths(root)
        git_available = True
    except SpecError:
        git_available = False
    if git_available:
        try:
            if source_ids is None or source_ids:
                result.update(
                    source_change_impact(root, old.commit or "HEAD", new.commit, old, new)
                )
            result["source_impact_complete"] = True
        except SpecError as error:
            result["notes"].append("Linked-file impact unavailable: " + str(error))
    else:
        result["notes"].append(
            "No Git comparison available: synthetic empty base; base source version unavailable."
        )
    result["source_resolutions"] = source_comparisons(
        root,
        old,
        new,
        git_available=git_available,
        node_ids=source_ids,
    )
    result.update(source_contract_impact(old, new, result["source_resolutions"]))
    result["affected"] = sorted(set(result["affected"]) | set(result["source_contract_affected"]))
    if comparison.display is not None:
        comparison.result = scope_result(result, set(comparison.display.nodes))
    return comparison


def comparison_graph(base: Snapshot, target: Snapshot) -> Graph:
    """Target records plus base-only ghosts, each retaining its own parents.

    No current record has a deleted parent, so paths entering ghosts cannot return
    to current nodes. This is acyclic, unlike the full old/new edge union. It is a
    display projection: new shortcuts, changed types and distinct roots are valid.
    """
    current = {n.id: n for n in target.nodes}
    nodes = {n.id: n for n in base.nodes} | current
    parents = {i: set(n.parents) for i, n in nodes.items()}
    children = {i: set() for i in nodes}
    for child, incoming in parents.items():
        for parent in incoming:
            children[parent].add(child)
    order = list(target.graph.order) if target.graph else []
    if base.graph:
        order.extend(i for i in base.graph.order if i not in current)
    return Graph(nodes, parents, children, order)


def _roots(graph: Graph, included: set[str]) -> list[str]:
    return sorted(i for i in included if not any(p in included for p in graph.parents[i]))


def last_occurrence_parents(graph: Graph, included: set[str] | None = None) -> dict[str, str]:
    """Assign last unfolded occurrences in an acyclic display projection.

    Right-to-left DFS over sorted roots/children prunes earlier unfolded paths.
    """
    included = set(graph.nodes) if included is None else included
    seen: set[str] = set()
    parents: dict[str, str] = {}
    for root in reversed(_roots(graph, included)):
        seen.add(root)
        stack = [
            (root, iter(sorted((c for c in graph.children[root] if c in included), reverse=True)))
        ]
        while stack:
            parent, children = stack[-1]
            child = next(children, None)
            if child is None:
                stack.pop()
            elif child not in seen:
                seen.add(child)
                parents[child] = parent
                stack.append(
                    (
                        child,
                        iter(
                            sorted(
                                (c for c in graph.children[child] if c in included), reverse=True
                            )
                        ),
                    )
                )
    return parents


def tree_entries(graph: Graph, included: set[str] | None = None):
    """Yield (id, reference, branch, continuation) using two-column tree rails."""
    forest = included is not None
    included = set(graph.nodes) if included is None else included
    parents = last_occurrence_parents(graph, included)
    roots = _roots(graph, included)
    if not roots:
        return

    def frame(node_id, prefix, children):
        return node_id, prefix, iter(children), children[-1] if children else None

    stack = [frame(None, "", roots)]
    while stack:
        parent, prefix, children, last_child = stack[-1]
        child = next(children, None)
        if child is None:
            stack.pop()
            continue
        last = child == last_child
        unbranched = parent is None and not forest
        branch = "" if unbranched else prefix + ("└─" if last else "├─")
        continuation = "" if unbranched else prefix + ("  " if last else "│ ")
        reference = parents.get(child) != parent
        yield child, reference, branch, continuation
        if not reference:
            descendants = sorted(c for c in graph.children[child] if c in included)
            stack.append(frame(child, "" if unbranched else continuation, descendants))


def source_item(row: dict) -> str:
    """Show one location; permitted contract changes need no annotation."""
    removed = row["declaration"] == "-"
    chosen, other = (row["base"], row["target"]) if removed else (row["target"], row["base"])
    path = chosen["path"]
    label = path if all(c.isalnum() or c in "/._-" for c in path) else json_text(path)
    if chosen["text_available"]:
        spans = ",".join(str(a) if a == b else f"{a}-{b}" for a, b in chosen["ranges"])
        label += ":" + (spans or "empty")
    hints = []
    if row["declaration"] != "=":
        hints.append("ref" + row["declaration"])
    restored = row["contract"] == "changed" and contract_state(row["target"]) == "valid"
    if restored:
        hints.append(
            "file added"
            if row["target"]["mode"] == "file" and row["base"]["outcome"] == "missing"
            else "restored"
        )

    def issue(value):
        if contract_state(value) == "valid":
            return None
        return value["outcome"] if value["outcome"] in BAD_OUTCOMES else "lines unavailable"

    current_issue, other_issue = issue(chosen), issue(other)
    if current_issue:
        hints.append(current_issue)
    if other_issue and other_issue != current_issue:
        if not (restored and not removed and other_issue == "missing"):
            hints.append(("target " if removed else "base ") + other_issue)
    suffix = " [" + "; ".join(hints) + "]" if hints else ""
    return label + suffix


def source_line(row: dict) -> str:
    """Present one source occurrence on a human-readable metadata line."""
    return "sources: " + source_item(row)


def body_line(body: str) -> str:
    """Flatten LF/CRLF runs without truncating text or parsing Markdown."""
    return re.sub(
        r"\n+",
        lambda match: " " if len(match[0]) == 1 else " ¶ ",
        body.replace("\r\n", "\n"),
    )


def query_lines(comparison: QueryComparison, *, human: bool = False) -> Iterator[str]:
    old, new, result = comparison.base, comparison.target, comparison.result
    before = {n.id: n for n in old.nodes}
    after = {n.id: n for n in new.nodes}
    changes = {c["id"]: c["kind"] for c in result["changes"]}
    affected = set(result["source_contract_affected"])
    file_changed = {f["path"] for f in result["file_changes"]}
    sources = defaultdict(list)
    for row in result["source_resolutions"]:
        sources[row["id"]].append(row)
    base_label = result["base_ref"]
    if not old.nodes and result["base_commit"] is None:
        base_label += " (empty)"
    yield f"{base_label} → {result['target_ref']}"
    if selection := result.get("selection"):
        if selection.get("with_ancestors"):
            yield (
                f"Subgraph: {len(selection['matched_ids'])}/{selection['population']} matches + "
                f"{len(selection['ancestor_ids'])} ancestors; root {selection['root']}"
            )
            if omitted := selection["surrounding"]["omitted_ids"]:
                yield "Surrounding IDs (bodies omitted): " + ", ".join(omitted)
        else:
            yield (
                f"Subgraph: {len(selection['ids'])}/{selection['population']} nodes; "
                f"root {selection['root']}"
            )
    for note in result["notes"]:
        yield "NOTE: " + note

    def record(node_id):
        a, b = before.get(node_id), after.get(node_id)
        node = b or a
        kind = changes.get(node_id)
        hints = [STATUS[kind]] if kind else []
        if node_id in affected:
            hints.append("source-changed")
        if not kind and any(n and n.path in file_changed for n in (a, b)):
            hints.append("file-only")
        header = f"{node.type} {node.id}"
        if node.parents:
            header += " @ " + ", ".join(sorted(node.parents))
        return header + (" [" + " ".join(hints) + "]" if hints else "")

    def contents(node_id):
        node = after.get(node_id) or before[node_id]
        metadata = []
        if node.format_version is not None:
            metadata.append(f"format_version: {node.format_version}")
        if node.extensions:
            metadata.append("extensions: " + json_text(node.extensions))
        rows = sources[node_id]
        if human:
            metadata.extend(source_line(row) for row in rows)
        elif rows:
            metadata.append("sources: " + ", ".join(source_item(row) for row in rows))
        yield from metadata
        if metadata:
            yield ""
        # Originals stay intact in JSON and diff. The CLI applies shared
        # terminal-control escaping to either text presentation.
        if human:
            yield from node.body.replace("\r\n", "\n").split("\n")
        else:
            yield body_line(node.body)

    def tree(graph):
        for node_id, reference, branch, continuation in tree_entries(graph):
            if reference:
                yield branch + f"↪ {node_id} ↓"
            else:
                yield branch + record(node_id)
                for line in contents(node_id):
                    yield continuation + line

    yield from tree(
        comparison.display if comparison.display is not None else comparison_graph(old, new)
    )


def render_query(comparison: QueryComparison, *, human: bool = False) -> str:
    return "\n".join(query_lines(comparison, human=human))

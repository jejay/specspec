"""Rooted query selection: shared DAG metrics, exact quotas and scoped records."""

from __future__ import annotations

import heapq
import re
from collections.abc import Iterable
from dataclasses import dataclass
from fractions import Fraction

from .graph import Graph
from .model import Diagnostic, SpecError

METRICS = ("min-distance", "max-distance", "influence")


@dataclass(frozen=True)
class Limit:
    text: str
    value: int | Fraction
    percent: bool = False

    @classmethod
    def parse(cls, text: str, metric: str) -> Limit:
        percent = text.endswith("%")
        pattern = r"(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)%" if percent else r"[0-9]+"
        if len(text) <= 64 and re.fullmatch(pattern, text):
            value = Fraction(text[:-1]) if percent else int(text)
            if not percent or value <= 100:
                return cls(text, value, percent)
        raise SpecError(
            [Diagnostic("QUERY", f"--{metric} requires a nonnegative integer or 0% to 100%.")],
            2,
        )

    def count(self, population: int) -> int:
        assert self.percent
        fraction = self.value * population / 100
        return -(-fraction.numerator // fraction.denominator)


def reachable(graph: Graph, seeds: Iterable[str], *, ancestors=False) -> set[str]:
    """One iterative multi-source walk, including existing seeds."""
    adjacency = graph.parents if ancestors else graph.children
    seen: set[str] = set()
    pending = [node_id for node_id in seeds if node_id in graph.nodes]
    while pending:
        current = pending.pop()
        if current not in seen:
            seen.add(current)
            pending.extend(adjacency[current])
    return seen


def metric_values(
    graph: Graph, root: str, population: set[str], requested: set[str]
) -> dict[str, dict[str, int]]:
    """One forward distance pass and, only if needed, one reverse influence pass.

    The population is descendant-closed. Stored strict-descendant bitsets omit
    leaf rows and are released after their last in-population parent consumes them.
    No path unfolding or per-node descendant searches are needed.
    """
    result: dict[str, dict[str, int]] = {}
    order = [node_id for node_id in graph.order if node_id in population]
    if len(order) != len(population):
        # A cycle outside this rooted scope must not invalidate its finite metrics.
        remaining = {i: len(graph.parents[i] & population) for i in population}
        order = sorted(i for i in population if not remaining[i])
        for id in order:
            for child in sorted(graph.children[id] & population):
                remaining[child] -= 1
                if remaining[child] == 0:
                    order.append(child)
    cyclic = len(order) != len(population)
    if cyclic and "max-distance" in requested:
        raise SpecError(
            [
                Diagnostic(
                    "METRIC",
                    "Maximum distance is unavailable in a cyclic rooted scope; "
                    "inspect query --issues.",
                )
            ]
        )
    if cyclic:
        result = {}
        if "min-distance" in requested:
            distances, queue = {root: 0}, [root]
            for node_id in queue:
                for child in sorted(graph.children[node_id]):
                    if child in population and child not in distances:
                        distances[child] = distances[node_id] + 1
                        queue.append(child)
            result["min-distance"] = distances
        if "influence" in requested:
            result["influence"] = {i: len(reachable(graph, [i])) for i in population}
        return result
    if requested & {"min-distance", "max-distance"}:
        minimum = {root: 0} if "min-distance" in requested else {}
        maximum = {root: 0} if "max-distance" in requested else {}
        for node_id in order:
            low = minimum[node_id] + 1 if minimum else 0
            high = maximum[node_id] + 1 if maximum else 0
            for child in graph.children[node_id]:
                if minimum:
                    minimum[child] = min(minimum.get(child, low), low)
                if maximum:
                    maximum[child] = max(maximum.get(child, high), high)
        if "min-distance" in requested:
            result["min-distance"] = minimum
        if "max-distance" in requested:
            result["max-distance"] = maximum
    if "influence" in requested:
        positions = {node_id: index for index, node_id in enumerate(order)}
        consumers = {i: len(graph.parents[i] & population) for i in order}
        masks: dict[str, int] = {}
        influence = {}
        for node_id in reversed(order):
            mask = 0
            for child in graph.children[node_id]:
                mask |= (1 << positions[child]) | masks.get(child, 0)
                consumers[child] -= 1
                if not consumers[child]:
                    masks.pop(child, None)
            influence[node_id] = mask.bit_count() + 1
            if mask and consumers[node_id]:
                masks[node_id] = mask
        result["influence"] = influence
    return result


def induced(graph: Graph, included: set[str]) -> Graph:
    """A display view, not a new canonical graph; node parent declarations stay full."""
    return Graph(
        {i: graph.nodes[i] for i in included},
        {i: graph.parents[i] & included for i in included},
        {i: graph.children[i] & included for i in included},
        [i for i in graph.order if i in included],
    )


def select_graph(
    graph: Graph, root: str, limits: dict[str, Limit], *, with_ancestors: bool = False
) -> tuple[Graph, dict]:
    if root not in graph.nodes:
        raise SpecError([Diagnostic("QUERY", f"No query root with full ID {root}.")], 2)
    population = reachable(graph, [root])
    quotas = {m: limit.count(len(population)) for m, limit in limits.items() if limit.percent}
    requested = {m for m, limit in limits.items() if not limit.percent or quotas[m]}
    values = metric_values(graph, root, population, requested) if requested else {}
    included: set[str] = set() if limits else set(population)
    queries = []
    for metric in METRICS:
        if metric not in limits:
            continue
        limit = limits[metric]
        counts = values.get(metric, {})

        def priority(node_id, counts=counts, reverse=metric == "influence"):
            value = counts[node_id]
            return (-value if reverse else value), node_id

        if limit.percent:
            ordered = heapq.nsmallest(quotas[metric], counts, key=priority)
        else:
            admitted = (
                i
                for i, value in counts.items()
                if (value >= limit.value if metric == "influence" else value <= limit.value)
            )
            ordered = sorted(admitted, key=priority)
        included.update(ordered)
        queries.append(
            {
                "metric": metric,
                "limit": limit.text,
                "nodes": [{"id": i, "value": counts[i]} for i in ordered],
            }
        )
    completion = {}
    if with_ancestors:
        matched = included
        included = reachable(graph, matched, ancestors=True)
        parents, children, siblings = set(), set(), set()
        for node_id in matched:
            parents.update(graph.parents[node_id])
            children.update(graph.children[node_id])
        for parent in parents:
            siblings.update(graph.children[parent])
        completion = {
            "with_ancestors": True,
            "matched_ids": sorted(matched),
            "ancestor_ids": sorted(included - matched),
            "surrounding": {
                "child_ids": sorted(children - included),
                "sibling_ids": sorted(siblings - included),
                "omitted_ids": sorted((children | siblings) - included),
            },
        }
    view = induced(graph, included)
    return view, {
        "root": root,
        "population": len(population),
        "ids": sorted(included),
        "edges": view.edges(),
        "queries": queries,
        "partial": included != graph.nodes.keys(),
        **completion,
    }


def select_issues(graph: Graph, seeds: set[str], *, with_ancestors=False):
    matched = seeds & graph.nodes.keys()
    included = reachable(graph, matched, ancestors=True) if with_ancestors else matched
    parents = set().union(*(graph.parents[i] for i in matched)) if matched else set()
    children = set().union(*(graph.children[i] for i in matched)) if matched else set()
    siblings = set().union(*(graph.children[i] for i in parents)) if parents else set()
    view = induced(graph, included)
    selection = {
        "root": "issues",
        "population": len(graph.nodes),
        "ids": sorted(included),
        "edges": view.edges(),
        "queries": [],
        "partial": included != graph.nodes.keys(),
        "matched_ids": sorted(matched),
        "ancestor_ids": sorted(included - matched),
        "issue_ids": sorted(matched),
    }
    if with_ancestors:
        selection.update(
            with_ancestors=True,
            surrounding={
                "child_ids": sorted(children - included),
                "sibling_ids": sorted(siblings - included),
                "omitted_ids": sorted((children | siblings) - included),
            },
        )
    return view, selection


def scope_result(result: dict, included: set[str]) -> dict:
    """Keep selected bindings and complete boundary references/evidence in API 7."""
    result = dict(result)
    paths, parents = set(), set()
    for side in ("base", "target"):
        snapshot = result[side]
        nodes = [n for n in snapshot["nodes"] if n["id"] in included]
        paths.update(n["path"] for n in nodes)
        parents.update(p for n in nodes for p in n["parents"])
        result[side] = {
            **snapshot,
            "nodes": nodes,
            "edges": [edge for edge in snapshot["edges"] if edge[1] in included],
        }
    result["selection"]["boundary_parents"] = sorted(parents - included)
    result["changes"] = [c for c in result["changes"] if c["id"] in included]
    result["file_changes"] = [c for c in result["file_changes"] if c["path"] in paths]
    for key in ("added_edges", "removed_edges"):
        result[key] = [edge for edge in result[key] if edge[1] in included]
    for key in ("affected", "source_affected", "source_contract_affected"):
        result[key] = sorted(set(result[key]) & included)
    evidence = set(result["selection"]["source_evidence_ids"])
    result["source_changes"] = [
        {**change, "implementation_ids": sorted(evidence & set(change["implementation_ids"]))}
        for change in result["source_changes"]
        if evidence.intersection(change["implementation_ids"])
    ]
    return result

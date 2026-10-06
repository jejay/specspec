"""Pure graph checks and deterministic traversals."""

from __future__ import annotations

import heapq
from dataclasses import dataclass

from .model import Diagnostic, SpecNode


@dataclass
class Graph:
    nodes: dict[str, SpecNode]
    parents: dict[str, set[str]]
    children: dict[str, set[str]]
    order: list[str]

    def closure(self, node_id: str, *, ancestors: bool = False) -> set[str]:
        adjacency = self.parents if ancestors else self.children
        visited: set[str] = set()
        pending = list(adjacency.get(node_id, set()))
        while pending:
            current = pending.pop()
            if current in visited or current == node_id:
                continue
            visited.add(current)
            pending.extend(adjacency.get(current, set()) - visited)
        return visited

    def edges(self) -> list[list[str]]:
        return sorted(
            [parent, child] for child, parents in self.parents.items() for parent in parents
        )

    def cycle(self) -> list[str]:
        # Iterative DFS avoids recursion limits on long specification chains.
        color: dict[str, int] = {}
        for start in sorted(self.nodes):
            if color.get(start):
                continue
            trail = [start]
            positions = {start: 0}
            color[start] = 1
            stack = [(start, iter(sorted(self.children[start])))]
            while stack:
                current, neighbors = stack[-1]
                child = next(neighbors, None)
                if child is None:
                    color[current] = 2
                    stack.pop()
                    positions.pop(trail.pop())
                elif color.get(child) == 1:
                    return trail[positions[child] :] + [child]
                elif not color.get(child):
                    color[child] = 1
                    positions[child] = len(trail)
                    trail.append(child)
                    stack.append((child, iter(sorted(self.children[child]))))
        return []


def build_graph(nodes: list[SpecNode]) -> tuple[Graph, list[Diagnostic]]:
    by_id = {node.id: node for node in nodes}
    parents = {node.id: set() for node in nodes}
    children = {node.id: set() for node in nodes}
    diagnostics: list[Diagnostic] = []

    def error(node: SpecNode, code: str, message: str) -> None:
        diagnostics.append(Diagnostic(code, message, node.path, node.id))

    manifestos = [node for node in nodes if node.type == "manifesto"]
    if len(manifestos) != 1:
        diagnostics.append(Diagnostic("ROOT", "Exactly one manifesto is required."))
    for node in nodes:
        if node.type == "manifesto":
            if node.parents:
                error(node, "PARENTS", "The manifesto cannot have parents.")
            if node.status != "accepted":
                error(node, "STATUS", "The manifesto must remain accepted.")
        elif not node.parents:
            error(node, "PARENTS", "A non-manifesto node needs at least one parent.")
        for parent_id in node.parents:
            parent = by_id.get(parent_id)
            if parent is None:
                error(
                    node,
                    "REFERENCE",
                    f"Missing parent {parent_id}; restore it or change the reference.",
                )
                continue
            parents[node.id].add(parent_id)
            children[parent_id].add(node.id)
            if parent_id == node.id:
                error(node, "SELF_REFERENCE", "A node cannot be its own parent.")
            if parent.type == "implementation":
                error(node, "PARENT_TYPE", "Implementation nodes cannot have children.")
            if node.type == "implementation" and parent.type != "requirement":
                error(node, "PARENT_TYPE", "Implementations need requirement parents.")
            if node.status == "accepted" and parent.status != "accepted":
                error(node, "STATUS", f"Accept parent {parent_id} before accepting its child.")
            elif node.status != "retired" and parent.status == "retired":
                error(node, "STATUS", f"Live nodes cannot depend on retired parent {parent_id}.")
    graph = Graph(by_id, parents, children, [])
    indegrees = {node_id: len(incoming) for node_id, incoming in parents.items()}
    ready = [node_id for node_id, degree in indegrees.items() if degree == 0]
    heapq.heapify(ready)
    while ready:
        node_id = heapq.heappop(ready)
        graph.order.append(node_id)
        for child in sorted(children[node_id]):
            indegrees[child] -= 1
            if indegrees[child] == 0:
                heapq.heappush(ready, child)
    if len(graph.order) != len(nodes):
        witness = graph.cycle()
        diagnostics.append(Diagnostic("CYCLE", "Cycle: " + " -> ".join(witness)))
    if len(manifestos) == 1:
        root_id = manifestos[0].id
        reachable = graph.closure(root_id) | {root_id}
        for node in nodes:
            if node.id not in reachable:
                error(node, "UNREACHABLE", "Node is not reachable from the manifesto.")
    return graph, diagnostics

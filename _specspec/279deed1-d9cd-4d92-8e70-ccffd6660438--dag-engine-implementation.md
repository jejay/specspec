---
id: 279deed1-d9cd-4d92-8e70-ccffd6660438
type: implementation
status: proposed
parents:
- 4d1f2eee-8125-4e3f-b9b4-649517875d87
- 6c457b0a-654e-4545-a4b4-667f467be4f3
sources:
- path: src/specspec/graph.py
  symbol: build_graph
- path: src/specspec/graph.py
  symbol: Graph.closure
- path: tests/test_core.py
managed_hash: cb7e8d2d10b402b8ef74017e21876ff0a02ae3b125010e889d1cf261c1583e72
---
# Index and validate the requirement DAG

`build_graph` builds node/parent/child dictionaries, checks the rooted type grammar
and lifecycle dependencies, and computes deterministic heap-based Kahn order.
Iterative traversal supplies context/impact closures and an explicit cycle witness
without depending on Python's recursion limit.

Verification includes multi-parent diamonds, generated DAGs, injected cycles, long
chains, invalid parent types, missing references, and lifecycle failures. These
checks establish graph structure, not semantic fulfillment of a parent's text.

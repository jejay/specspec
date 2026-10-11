---
id: i6Y3Z7I=
type: implementation
parents:
- DiIJxaQ=
- LvYBN_4=
- apEb_pM=
sources:
- path: src/specspec/graph.py
  symbol: Graph.closure
- path: src/specspec/graph.py
  symbol: build_graph
- path: tests/test_core.py
- path: tests/test_core.py
  symbol: test_withdrawal_batches_are_explicit_and_are_not_approval
---
# Index and validate the requirement DAG without approval gates

build_graph builds node/parent/child dictionaries, validates the rooted node grammar,
and computes deterministic heap-based Kahn order. Iterative traversal supplies
context/impact closures and a concrete cycle witness without recursion limits.
There are no accepted-parent or proposed/accepted selection rules.

Withdrawal preserves explanations: the manifesto cannot be retired, and a live node
cannot depend on a retired parent. Explicit retirement/restoration batches must
leave these relationships valid; they do not claim review or correctness.

Tests cover multi-parent diamonds, generated DAGs, injected cycles, long chains,
invalid parent types, missing references, explicit withdrawal/restoration batches,
and live graphs whose nodes have no approval metadata. These checks establish
structure, not semantic fulfillment of a parent's text.

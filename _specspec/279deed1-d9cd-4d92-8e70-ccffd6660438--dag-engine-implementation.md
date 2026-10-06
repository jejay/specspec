---
id: 279deed1-d9cd-4d92-8e70-ccffd6660438
type: implementation
parents:
- 4d1f2eee-8125-4e3f-b9b4-649517875d87
- 6c457b0a-654e-4545-a4b4-667f467be4f3
- ca580dc7-c7fa-48bc-91b1-59243144a0bf
sources:
- path: src/specspec/graph.py
  symbol: Graph.closure
- path: src/specspec/graph.py
  symbol: build_graph
- path: tests/test_core.py
- path: tests/test_core.py
  symbol: test_withdrawal_batches_are_explicit_and_are_not_approval
managed_hash: 5dae50d9b12b8f31c526e3e61e24daf83814c734c81cc8eb216f5459f2fdca1d
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

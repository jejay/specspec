---
id: i6Y3Z7I=
type: implementation
parents:
- DiIJxaQ=
- LvYBN_4=
- apEb_pM=
sources:
- path: src/specspec/graph.py
- path: tests/test_core.py
---
# Index and validate the rooted DAG iteratively

`build_graph` validates node schemas, unique identities, parent references/types,
root reachability and terminal implementation grammar. It builds node/parent/child
maps and deterministic heap-based Kahn ordering. Iterative closure traversal and
cycle witnesses support deep/shared graphs.

The core checks are linear with deterministic ordering's O(V log V) heap cost.
Each invocation derives its graph from current files. Tests cover diamonds,
generated/deep DAGs, missing/unsafe parents and concrete cycles. Structural
validation supplies consistency evidence; binding fulfillment needs review.

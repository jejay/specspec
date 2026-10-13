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
  symbol: test_deletion_batches_are_explicit_physical_and_keep_the_remaining_dag_valid
- path: tests/test_core.py
---
## Current deletion-only correction

xu6W0c4=/5d5oDCM= supersede the earlier retired/withdrawal workflow below.
Current schema/API 5 removes the flag and all retire/restore/filter/metadata/badge
paths. Managed delete physically unlinks an explicit batch after DAG checks,
with journal new=null and original-byte/recovery safeguards. Default HEAD-relative
UI ghosts are derived base records, read-only/copyable through staging and gone
after commit; Git HEAD/ref watching refreshes both hosts. Native Delete requires
clean project documents; deleted buffers never resurrect files in overlay reads.
All earlier workflow/schema/test counts below are historical evidence. Gantt's
entire current corpus is rebuilt with 22 physical deletions/reasons in prior Git
commits and a 22-node HEAD, no flagged retained nodes. Earlier root explanations
are in Git, not retained retired files. Source regions/colors/shapes/camera/native
Save remain in scope; the separate current implementation record links actual tests.

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

---
id: YkxeXd0=
type: requirement
parents:
- 8O0LYEM=
- 2doGbqA=
---
# Batch metric selection and preserve relevant source evidence

Build the selected-record projection once, find the reachable population once and
reuse its topological order. Compute both requested distance bounds in one forward
pass. Compute self-inclusive influence only when required, in one reverse DAG pass
using integer descendant bitsets. Union bits rather than adding child counts;
release each child's stored bitset after its last parent consumes it. Leaf masks
need no stored bitset. This bounds live memory on chains and wide leaf fans.

Metric ranking over this population agrees with a child-frontier priority walk:
maximum distance increases on each edge, influence decreases, and every minimum
distance has a shortest-path predecessor one step nearer. Batch ranking with full
ID tie-breaks therefore preserves next-node semantics without unfolding paths or
rerunning graph searches, reads or source resolution per criterion. Apply absolute
predicates before sorting; percentage quotas may use bounded top-k selection.

Select before source work. Optional ancestor completion uses one multi-source
parent walk before constructing the final view; quotas retain their original
matched sets. Collect surrounding identities through deduplicated matched parents.
Resolve source evidence after completion, including other branches when necessary
for added ancestors' badges. Resolve declarations owned by selected nodes or their
descendants in either original revision, since excluded descendants can change a
selected ancestor's source badge. Merge graph reachability and ancestor propagation
per revision rather than repeating closure per node. Resolve each exact declaration
once per code version with the existing reader-local batches and budgets. Unrelated
branches and empty selections need no source resolution. JSON keeps all required
source evidence, including its owner IDs outside the visible binding set, while
selected affected sets remain scoped. Revision reads, code-version readers and
source comparisons are shared across every criterion and both text presentations.

Independent path, transitive-closure and literal priority-frontier oracles verify
sets and order, equality, quota rounding, duplicates/sharing and all criterion
combinations. Counting regressions verify graph passes and one read/metric/source
batch, alongside current-schema Gantt revisions, freshness and read-only checks.

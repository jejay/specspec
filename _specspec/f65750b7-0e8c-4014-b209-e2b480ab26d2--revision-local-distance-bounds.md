---
id: f65750b7-0e8c-4014-b209-e2b480ab26d2
type: requirement
parents:
- fc78af57-8c98-4dc5-9cc4-e590d4594cf2
- 2f6ee5bd-9014-4a0c-8677-53ecbab93f92
- 4d1f2eee-8125-4e3f-b9b4-649517875d87
- 51c3e963-674e-4d5d-bd7a-b8d63649e1c8
---
# Derive minimum and maximum directed path lengths per revision

Compute minimum distance with iterative breadth-first traversal from the manifesto.
Compute maximum distance with iterative topological dynamic programming over all
snapshot relationships, not the placement backbone or only visible neighbors.
Both count directed edges, with manifesto distance zero. Multiple-parent shortcuts
can make minimum smaller than maximum. Neither is confidence, review effort, or a
canonical stored score. Maximum agrees with full-root DAG rank, but is a snapshot
metric rather than a visible-subgraph placement instruction.

Deduplicate repeated edges. Missing/unreachable nodes have unknown distances and
a neutral fill. Defensive cyclic input must terminate; do not publish a finite
maximum for a cycle or a descendant whose parents cannot all be processed. Do not
combine base/target edges to compute paths: surviving nodes use target metrics,
removed nodes use base metrics, even when the display union has reverse cycles.

Keep the existing distance preference as minimum for compatibility; add a separate
maximum preference, retaining node-type coloring and obsolete-status fallback.
Use one palette indexed by the selected distance and explain shortest/longest paths
in the legend. Remove all on-node hop-distance badges/text, including focused
parent and expanded cards. Retain downstream, Git, and withdrawn labels. No color
switch changes node records, drafts/caret/original node contents, camera, routing, or positions.

Test unequal paths, multiple parents, deep iterative traversal, repeated edges,
unreachable/defensive cycles, revision isolation, both legends/preferences,
label absence, and native draft/selection preservation.

Origin: a separate metric/presentation conclusion implementing the user's two
distance modes and simpler cards; algorithms, preference keys, and palette reuse
are revisable choices.

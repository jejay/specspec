---
id: fbaee7c1-4c20-47ab-afd2-ae0503d428b5
type: requirement
status: proposed
parents:
- c93ab412-77b7-4849-a556-d8e3994b825b
- 18d1da0d-8bc3-4d58-8720-8ce194a74d1b
- e3494686-5da4-40f5-a622-f823c2e0c9b2
- 2b8a4bbc-d15a-4347-90b4-691abdeefaef
managed_hash: 6f508d811ebc42b1196936711ec83f7ad7dacc2c5b42d9c87a0ccc82a5ef51e7
---
# Reuse a layered graph engine while retaining safe native forms

Use Dagre's client-side directed layout in LR mode, with fixed world-space card
widths and measured intrinsic heights. Stable ID/edge ordering, relation-aware
ranking, crossing reduction, and long-edge waypoints determine the arrangement.
Do not pass viewport dimensions to the layout. Focused views use upstream nodes
on the left and downstream nodes on the right; forms remain native DOM elements.

Reuse d3-shape for horizontally tangent Bezier links at right output and left
input ports, retaining the layout engine's reserved paths through skipped ranks.
Keep those paths flat across full card-width bands before smoothing empty gaps;
this prevents smoothing from averaging away obstacle clearance. Preserve clear
direction and revision accents.
Preserve removed/reversed revision edges without interpreting the overlay as a
valid canonical DAG. Keep shortest-distance/downstream metrics on each snapshot.

React Flow, Rete, LiteGraph, ELK, and Dagre were considered. Dagre plus D3 separates
layout/navigation from canonical mutations and preserves the existing safe forms
without a React rewrite, computational socket engine, or Canvas text editor.
This is a scoped reuse choice, not a claim of having ported Blender to JavaScript.
Bundle dependencies locally, pin lockfile versions, and include license notices;
no CDN, remote renderer, project-supplied scripts, or runtime code generation.

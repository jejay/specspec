---
id: uAjln2M=
type: requirement
parents:
- DiIJxaQ=
---
# Keep direct links free of shortcuts and review what a changed chain passes on

The graph records the smallest set of direct links between intentions and conclusions. Every direct parent of a node adds ancestors that its other parents do not supply, so a direct parent is never at the same time an indirect one. The direct parents of a node may lie at different depths as long as none is an ancestor of another. All ancestors of a node are among its reasons.

An implementation realizes the part of its ancestors' intentions that its text states, and several implementations together may realize an intention completely. A change to a chain of links calls for reconsidering what follows from it further down. The possible effects are reviewed on both the previous and the resulting graph, including ancestors that a node has lost. A relationship that a node needs in its own right is put back deliberately in the new graph. A structurally consistent graph is evidence for the review, and whether the statements are fulfilled is judged apart from it.

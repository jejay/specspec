---
id: ee57a451-059d-426b-868e-e898c2503082
type: requirement
parents:
- adb5a4c8-f9c5-4bcc-b38b-8584d469cf25
- 003d697b-4104-4fdf-8e05-0db572c436d0
managed_hash: 781e724a5c34d52a7e15af712f76418c4d2394382388b6075a79c41b73c4d5cb
---
# Edit a selected node within its relationship context

Clicking a node opens a focused subgraph containing that node, its direct parents,
and its direct children instead of a separate editing sidebar. The selected node
expands to contain the relevant settings and inputs; its neighbors retain the
compact detail level used in the total graph. Provide a back action to return to
the total graph and allow navigation by selecting neighboring nodes.

Preserve managed editing, Git change context, drafts, and withdrawal history
in this presentation, without introducing an individual approval step.

Origin: the user's requested tree UI revision, 2026-10-04. This records requested
product behavior, not a chosen layout or rendering mechanism.

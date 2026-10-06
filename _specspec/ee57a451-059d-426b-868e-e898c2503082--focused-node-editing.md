---
id: ee57a451-059d-426b-868e-e898c2503082
type: requirement
status: accepted
parents:
- adb5a4c8-f9c5-4bcc-b38b-8584d469cf25
- 003d697b-4104-4fdf-8e05-0db572c436d0
managed_hash: f5cd208481dcc5083b62fc1b6e8f77c86d9988c1d184c0e6578ebc5ac80fe2ee
---
# Edit a selected node within its relationship context

Clicking a node opens a focused subgraph containing that node, its direct parents,
and its direct children instead of a separate editing sidebar. The selected node
expands to contain the relevant settings and inputs; its neighbors retain the
compact detail level used in the total graph. Provide a back action to return to
the total graph and allow navigation by selecting neighboring nodes.

Preserve the managed editing and explicit review actions in this new presentation.

Origin: the user's requested tree UI revision, 2026-10-04. This records requested
product behavior, not a chosen layout or rendering mechanism.

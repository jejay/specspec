---
id: ee57a451-059d-426b-868e-e898c2503082
type: requirement
parents:
- adb5a4c8-f9c5-4bcc-b38b-8584d469cf25
- 003d697b-4104-4fdf-8e05-0db572c436d0
managed_hash: 6c9cd479ba59684bd8bdf6f984b560881cb6abbc769a402a359720539cc39bab
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


The later Activity Bar request hosts the whole graph in VS Code's sidebar; this does not reinstate a separate settings sidebar alongside the graph. Settings still expand inside the selected node.

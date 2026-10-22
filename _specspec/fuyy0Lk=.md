---
id: fuyy0Lk=
type: requirement
parents:
- xu6W0c4=
- DiIJxaQ=
---
# Delete all descendants and warn about uncommitted affected nodes

Managed deletion removes the selected node and every directed descendant,
including children shared with outside parents and their descendants. Deduplicate
multiple paths and overlapping requested roots. Preserve outside parents.

Before deleting, warn about every affected node with uncommitted saved changes.
Staged additions/edits remain uncommitted. Committed deleted nodes retain D ghosts
through staging until commit; never-committed nodes have an empty HEAD membership.
Git retains removed reasoning and ordinary commit messages record the reasons.

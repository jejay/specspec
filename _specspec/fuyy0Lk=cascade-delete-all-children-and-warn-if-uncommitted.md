---
id: fuyy0Lk=
type: requirement
parents:
- xu6W0c4=
- DiIJxaQ=
---
# Delete every descendant, including shared children, and warn about uncommitted nodes

Deleting a node through SpecSpec also deletes all its children, at every depth.
This includes full children and partial children: a child with other parents is
still a child of the selected node and is deleted with it, along with its own
descendants. Multiple paths or requested roots do not duplicate deletion.

Before removing files, warn if the requested node or any affected descendant is
not committed. Staging is not committing; an added or edited staged node still
needs the warning. Keep the deletion-only model and HEAD-relative default graph:
committed nodes remain as D after deletion and staging, disappearing after commit.
Explain deletion reasons and retain earlier reasoning in normal Git history.

Origin: the user's follow-up in this conversation. This corrects the earlier
explicit-dependent-batch implementation choice, not the physical-deletion/HEAD
intention. Warning delivery and destructive-action confirmation are separately
specified mechanisms, not review states or per-node approval gates.

---
id: xu6W0c4=
type: requirement
parents:
- 3wsnEjk=
- ME4UXTA=
- SRsw2W0=
---
# Withdraw nodes by deleting files, not storing retirement states

Remove the withdrawal/retired status workflow. Withdrawing a node means deleting
its physical canonical Markdown file. Explain the reason in the Git commit;
Git history, not a retained-state flag, holds the earlier specification.

The default workspace graph always displays its difference to HEAD. A file deleted
from the workspace still appears as a deleted node in that view until the deletion
is committed. Staging does not make it vanish; after committing it no longer
belongs to HEAD or the workspace and vanishes from the default graph. Explicit
historical comparisons can still show earlier nodes. Do not invent review states.

Origin: the user's explicit simplification in this conversation, superseding the
withdrawal-flag conclusion apEb_pM=, not undoing risk-proportionate review or Git.

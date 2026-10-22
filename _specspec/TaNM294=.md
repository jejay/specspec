---
id: TaNM294=
type: requirement
parents:
- DG-JpDc=
- SRsw2W0=
---
# Associate a spotlight with its revision comparison

An owner or agent selects nodes and one message in a workspace/HEAD view or an
explicit comparison of workspace and commits or branches. The message can discuss
added, deleted, changed and unchanged nodes together. Selecting that spotlight in
either host switches the graph to its comparison and highlights the available
members, including deleted base nodes. The ordinary default is workspace versus
fresh HEAD. Git remains the source of committed node contents.

Workspace changes after capture produce a visible warning in CLI and UI. Keep the
best available highlighting by node identity even when versions drift or members
are absent. Spotlight records carry the comparison and references as local helper
data; committed revisions provide historical contents.

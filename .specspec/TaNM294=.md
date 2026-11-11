---
id: TaNM294=
type: requirement
parents:
- DG-JpDc=
- SRsw2W0=
---
# Tie each spotlight to the comparison in which it was made

An owner or an agent selects nodes and writes one message, either in the view of the working files against HEAD or in a chosen comparison of the working files, commits or branches. One message can speak about added, deleted, changed and unchanged nodes together. Selecting the spotlight in either graph editor switches the graph to that comparison and highlights the members that are available, including nodes that the base holds and the target deleted. The usual comparison is the working files against HEAD as it resolves at that moment. The content of committed nodes comes from Git.

When the working files change after a spotlight was captured, the command line and the editors show a warning. The members are highlighted by node ID as well as the displayed graph allows, also when their versions have drifted or some are absent. A spotlight record carries its comparison and its references as local helper data, and the committed revisions supply the earlier content.

---
id: SRsw2W0=
type: requirement
parents:
- eLTZ3sg=
- kpatAr8=
---
# Show in the graph what differs between the working files and a commit or between two commits

The graph editors show how the specification differs between two states. A view of the working files shows their difference from the commit that HEAD names at the moment of the read, and a user can compare two commits of their choice. The owner reads from the graph which nodes were added, modified or deleted and which links changed. The comparison works beside the Git integration of the editor that the graph runs in.

A node that changed itself is told apart from a node whose linked source files changed: the first carries the letter of its Git status, A for added, M for modified or D for deleted, and the second carries an informational cue. The fill color of a card and the cue for changed sources each have a meaning of their own, and each is explained on its own. The marks take the colors that the theme of that editor configures, and the standalone desktop app uses fitting defaults.

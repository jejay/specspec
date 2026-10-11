---
id: RlFT4io=
type: requirement
parents:
- qf5-4sc=
- t8RQMdE=
- PL1IogE=
---
# Darken graph context outside the hovered node's connections

When hovering a node, darken all nodes not connected to it and all connections
outside the highlighted connections. Retain the hovered node and its connected
neighbors as the readable relationship context. Leaving the node restores normal
appearance without selecting, editing, hiding or changing the graph.

Apply the behavior in overview and focused views, including expanded cards, in
both shared hosts. Preserve existing link highlighting, direction and Git cues.

Origin: the user's hover-darkening request in this conversation. Neighborhood
scope and rendering mechanisms are independently revisable technical choices.

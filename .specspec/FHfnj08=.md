---
id: FHfnj08=
type: requirement
parents:
- 7woeTpk=
- 6IzHBjQ=
---
# Compute the shortest and the longest distance from the manifesto for each revision on its own

The minimum distance of a node from the manifesto is computed by an iterative breadth-first search and the maximum distance by dynamic programming in topological order, both over all links of a revision. A distance counts directed links, and the manifesto has distance zero. A link that occurs twice counts once. A node that cannot be reached, or whose paths a cycle blocks, has an unknown distance and a neutral fill. The computation ends for every input, also for one that contains a cycle.

In a comparison a node that the target contains takes its distances from the target, and a deleted node takes them from the base. The distances follow from the complete graph of a revision. The union of both sides that a comparison draws and the forest that places the nodes are presentation. The minimum and the maximum distance are separate color meanings, and each view stores which one is selected. A switch of the color meaning leaves the node records, the form with its draft and text cursor, the camera, the routes and the positions in the world as they are.

---
id: tgHQyx4=
type: requirement
parents:
- 6EmKDz8=
- LtROyww=
- qf5-4sc=
- bOXyw00=
---
# Place the nodes with Dagre and curve the links with d3-shape, both bundled locally

Dagre places the nodes as a directed graph in layers from left to right. It receives the nodes and links in a stable order by ID and the measured widths and heights of the cards, and it reserves a lane for a link that spans several layers. The layout moves the cards alone, and the form of the selected node is the same DOM element before and after.

The links are Bézier curves from d3-shape. A link leaves a port on the right side of its parent and arrives at a port on the left side of its child, with a horizontal tangent at both ends. Its lane is flat across the full width of every column of cards that it passes, and it bends in the clear gaps between the columns. A link that Dagre was not given for the placement gets a corridor of its own, and a link of an earlier revision that points against the reading direction is drawn as well.

Dagre and D3 handle placement and navigation and change nothing of the graph itself, and the text and the controls of the cards are ordinary DOM elements of the shared renderer. Both libraries are bundled locally in pinned versions, together with the license notices of every package that the bundle contains.

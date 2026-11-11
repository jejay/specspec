---
id: 3jX0Rgk=
type: requirement
parents:
- aiuyGEs=
---
# Place each node beside one of its deepest parents and draw every link

The ranks come from all parents of a node. For the placement each node keeps one parent: among its parents in the rank directly before its own, the one whose ID sorts first. These links form a forest that preserves every rank, and Dagre places this forest compactly. Every relationship is drawn all the same, those of the node files and those of an earlier revision. The forest serves the placement alone, and the parents in the node files hold the complete graph of intentions and conclusions.

A forward link outside the forest crosses every column between its two cards through a nearby clear gap between the cards of that column. The lane outside a column, above or below it, is the fallback, and a link of an earlier revision that points against the reading direction runs around the outside of the graph. These routes are rules of thumb for a stable and readable picture, and they keep a cautious distance from the cards.

An ordinary compact card is 264×112 world units, the gap between two ranks is 140 units and the gap between neighbors within a rank is 44 units. Tests verify that headings and badges fit into the compact card and that the routes stay clear of the painted outlines of the cards. The round manifesto and an expanded card enter the layout with the sizes of their own shapes and contents.

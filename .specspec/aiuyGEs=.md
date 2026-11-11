---
id: aiuyGEs=
type: requirement
parents:
- U7wDQk0=
- tgHQyx4=
---
# Put every node in the column after its deepest parent, counted from the manifesto

The manifesto has rank zero, and every other node has a rank one higher than the highest rank among its parents. A rank is a column of the layout. A short branch thus stays near the manifesto, and every node stands after its deepest parent. Nodes and links enter the layout in a stable order by ID, and the spacing follows from the sizes of the cards themselves. The ranks serve the placement. The shortest distance that a color shows and the longest path over the complete graph of a revision are measures of their own, each with its own meaning.

The longest-path ranker of Dagre anchors its ranks at the nodes without children. The layout therefore hands Dagre the links of the placement reversed, with the rank direction from right to left, which anchors the ranks at the manifesto and preserves them. It then reverses the waypoints of the links into the visible direction from left to right.

In a comparison the ranks follow the links of the target, in the overview and in the view of a node that the target contains. The view of a selected node that the target deleted follows the links of the base. A link that only the other side of the comparison has is drawn over this layout. The display tolerates a cycle among the drawn links and shows both sides of the comparison, and a set of node files that is invalid in itself is reported apart from the picture.

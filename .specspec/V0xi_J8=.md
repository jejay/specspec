---
id: V0xi_J8=
type: requirement
parents:
- t8RQMdE=
- 6IzHBjQ=
- bOXyw00=
---
# Move the form into the expanded card of the selected node and count the unique descendants of each child

The selected node becomes an expanded card, and the one form of the editor, with the text, the parent links and the source links of the node, moves into it as the same DOM element. The direct parents and children of the node stand around it as compact cards. The Total graph action returns to the overview and keeps the draft, and selecting another node while the form has unsaved changes asks the owner to confirm that they are discarded. The form lists the actual parent links apart from the picker that offers candidates for Add parent, and choosing a candidate in the picker leaves the links as they are until Add parent is pressed.

Each child card shows the number of its unique descendants at every depth, counted iteratively and without the child itself. A leaf shows zero, and the totals of two children can overlap. Distances and relationships come from one revision: from the base for a deleted node and from the target for every other node. The links that only the base has are drawn over the graph and marked with what the comparison says about them. The counts and the layout are presentation that is derived from the links of the node files and lasts as long as the view.

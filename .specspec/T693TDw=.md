---
id: T693TDw=
type: requirement
parents:
- kiOMI7I=
---
# Print the graph as a tree with each node's full record at its last occurrence

The readable `query` prints the graph as a tree. Children are ordered by ascending full ID, compared case-sensitively. The tree is the graph unfolded depth-first from left to right, so a node with several parents occurs once under each of them. The complete record of a node is printed at its last occurrence, and each earlier occurrence is a short forward reference that is left unexpanded, written `↪ ID ↓`. The full record of every parent therefore comes before the full record of its child. The parent under which a record is printed is found by an iterative depth-first walk from right to left: the parent under which the walk first meets a node is the one, and where the walk meets the node again it goes no deeper. The tree is then printed from left to right. After sorting, the walk takes time in proportion to nodes plus edges, uses explicit stacks, and the unfolded tree stays a concept that is never built. The last occurrence follows from the order of the walk alone, wherever the deepest parent of the node lies.

The order applies to the display graph of a comparison, which holds the selected nodes of both revisions. The structured records of each side keep every selected node with all its parents, so that each side can be reconstructed, and a query without a selection covers the whole comparison. Rails of Unicode line characters stand before the lines that are displayed. A full header gives the type, the full node ID and all direct parents. The reading holds the complete text of every current and deleted node in compact form, with sparse hints of what changed between the revisions and in a presentation that is safe for a terminal. The structured records of the comparison hold the complete logical bodies with their whitespace, and CRLF in parsed text is turned into LF. Frontmatter comments, the exact spelling and the literal line ends are available in the node files and through a raw `query`, and `diff` compares the logical text of the node files.

`query` diagnoses the graphs of the selected revisions and reads linked code from those same versions. A part of the graph that is invalid is printed in a finite form that is the same on every run and safe against cycles, with the complete text of its nodes. `--json` gives records of the application protocol from which the selected part can be reconstructed, and an explicit subgraph names its population, the parents on its boundary and the edges inside it.

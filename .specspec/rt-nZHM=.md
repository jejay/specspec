---
id: rt-nZHM=
type: requirement
parents:
- kiOMI7I=
---
# Select a part of the graph from a root by distance or by influence

`query` reads the whole graph or selects a subgraph that starts at the manifesto or at a node that is named. The nodes are taken in the order of one of three measures: the minimum distance from the root, the maximum distance from the root, or the influence, which is the absolute number of a node itself plus its unique descendants, with no logarithm applied. For the distances the smaller values come first, and for influence the larger ones.

A limit given as a number includes the nodes that equal it: `--max-distance 2` selects the root, at distance zero, and the first two levels. A limit given as a percentage stops at that share of the size of the graph, in the order of the measure: `--max-distance 50%` selects 62 of 124 nodes. A node that several paths reach counts once. With two or all three measures the result is the union of the subgraphs that each selects on its own. The selected nodes appear with their complete text and their relationships. A selection leaves the rest of a query as it is: the compared revisions, the reading of source links and the read-only nature.

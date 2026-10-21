---
id: rt-nZHM=
type: requirement
parents:
- kiOMI7I=
---
# Select rooted query subgraphs by distance or influence

Query can read the whole graph or search a subgraph starting at the manifesto or
a specified node. Order next-node selection by minimum distance, maximum distance
or absolute non-logarithmic influence, counting self plus unique descendants.
Distances prioritize smaller values; influence prioritizes larger values.

An absolute stop criterion includes equality: --max-distance 2 includes the root
at zero and the first two levels. A percentage stops at that fraction of graph
size in metric-priority order: --max-distance 50% selects 62 of 124 nodes. Shared
nodes count once. When two or all three metrics are supplied, return the union of
the independently selected subgraphs. Present complete selected bindings and
relationships, preserving the query's revision, source and read-only contracts.

Keep queries quick by batching graph metrics and reusing selection, revision and
source work within each invocation. Resolve saved data freshly on each call.

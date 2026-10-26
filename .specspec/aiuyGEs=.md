---
id: aiuyGEs=
type: requirement
parents:
- U7wDQk0=
- tgHQyx4=
---
# Use earliest ranks anchored at the manifesto

Assign manifesto rank zero and each primary node one plus the maximum rank of its
primary parents. This keeps short branches near the origin while placing a child
after its deepest parent. Stable ID ordering and intrinsic spacing determine layout.
Shortest-path colors and full-snapshot longest paths have their own semantic meaning.

Adapt Dagre's RL longest-path ranker with reversed rank-preserving input, then reverse
waypoints to visible LR direction. Rank target primary relationships for surviving
views and base context for a removed selection. Historical extra links are overlays.
Cycle-tolerant display keeps comparison context visible and reports invalid canonical
snapshots separately.

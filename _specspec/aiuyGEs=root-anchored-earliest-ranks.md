---
id: aiuyGEs=
type: requirement
parents:
- U7wDQk0=
- tgHQyx4=
---
# Anchor layered ranks at the origin rather than shared sinks

For an acyclic displayed graph, assign the manifesto rank zero and each node the
earliest rank strictly after all its displayed parents: one plus the maximum
parent rank. A short branch or a new shared sink must not pull earlier intentions
rightward. This is not shortest manifesto distance: a multi-parent node still
needs to follow its deepest parent. Minimum-distance color follows shortest paths;
maximum-distance color follows full-snapshot longest paths, not only visible
placement constraints. Neither requires a repeated hop badge on the card.

Reuse Dagre's longest-path ranker on a reversed rank-preserving input graph with
an RL engine direction; the compact-backbone proposal separately adapts placement. That adapter yields the original graph's earliest-source ranks while
keeping visible development LR; reverse engine waypoints back to original edge
direction. Retain stable ID ordering, crossing reduction and obstacle corridors,
with more compact intrinsic spacing. Do not use viewport size to compress cards.

Rank surviving relationships from the target graph. Historical removed links are
an overlay, not constraints that can drag the live origin away or turn a cyclic
revision union into a canonical DAG. Base-only nodes may retain historical context
and routes. Keep cycle-tolerant presentation without claiming validity of a union.

This changes the earlier sink-biased heuristic, not the canonical graph structure.
Regression fixtures should include a shallow branch sharing a deep sink and the
actual repository's manifesto children, not only simple chains and diamonds.

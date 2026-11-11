---
id: FU5NaYc=
type: requirement
parents:
- MPOzb8A=
- 93sqYPw=
- LjbEgSo=
- ZIpsXgo=
---
# Deepen and reconcile the specification when asked to plan it

A request to draw or change the graph starts agent planning. The agent reads the existing graph, what the owner changed, the Git history and the tandem rounds, and commits the owner's open edits first. With `specspec add`, `update` and `delete` it builds the most precise graph that this understanding supports: it completes the depth that building needs, fills breadth where the owner evidently left a gap for it, gives every conclusion a node of its own and says how each serves its intentions.

When it merges or removes nodes, it looks at what hangs beneath them and reconnects what stays. It validates the whole graph and the exact staged state. The planning request also allows it to commit the result as `Agent specspec changes: <description>`; every other commit follows the project's own rules. Its summary names the intentions it read into the owner's words, its own conclusions, open questions, what is not built yet and the affected nodes. Where earlier commits hold nodes in a format that the tools no longer read, the agent plans from the current files.

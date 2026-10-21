---
id: T693TDw=
type: requirement
parents:
- kiOMI7I=
---
# Place full records at the last occurrence of an ordered unfolded walk

Order children by ascending full case-sensitive ID. In a conceptual left-to-right
depth-first unfolding, print a complete record at its last occurrence and short
unexpanded forward references at earlier occurrences, using ↪ ID ↓. Full parents
precede full children. Assign display parents with iterative right-to-left DFS,
recording first encounters and pruning earlier paths, then print left-to-right.
Traversal is O(V+E) after sorting, with explicit stacks and conceptual unfolding.
Last occurrence follows traversal independently of maximum graph depth.

Apply this ordering to the selected-record display projection of a comparison. Retain
every node from either side and every relationship in reconstructible side records.
Unicode continuation rails prefix displayed data. Full headers give type, filename
stem and all direct parents. Preserve complete current/deleted binding text and
whitespace with sparse revision hints and safe terminal presentation. Structured
comparison records retain both versions. Canonical comments, spelling and literal
line endings remain available through node files and the dedicated diff command.

Query validates the selected saved graphs and reads code from those versions.
--json uses the complete reconstructible API-6 comparison projection. Node format
6 and existing application operations retain their definitions.

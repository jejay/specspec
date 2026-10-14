---
id: wAp9Qz8=
type: requirement
parents:
- tGpRMLM=
- Yfy0414=
---
# Read canonical Git objects in bounded metadata and content batches

List literal NUL-delimited current tree or exact-index entries and deduplicate their
object addresses for bounded batch-check/content requests. Preserve per-path entry,
mode, stage/conflict, nesting, size, object availability and schema diagnostics.
Inspect types/sizes before reading bodies; check ordered object identities, exact
binary framing, truncation, exits and finite request/output/time budgets. Handle
SHA-1/SHA-256, absent graphs and genuine unborn HEAD through the existing semantics.
Chunk large graphs rather than silently truncating them. Git reads retain checkout,
index, object and ref ownership with the user and use local object availability.

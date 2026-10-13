---
id: jsIUeP0=
type: requirement
parents:
- v6xn2GU=
- Yfy0414=
- qowy5AI=
---
# Anchor source snapshots and derive target locations

A source hint keeps a project-relative path and optional descriptive symbol.
Whole-file hints are available. Region hints add a full immutable Git blob ID,
strict/expanding mode and multiple positive inclusive 1-based ranges. Derive their
worktree/index/revision positions from bounded textual diff/context and rename
assistance. Report missing/deleted objects, ambiguity and uncertain mapping.

Capture from committed HEAD or an explicit staged index. Retain the anchor through
an existing commit tree or the upcoming commit's staged source tree; blob references
in Markdown are textual addresses while Git trees supply reachability. Support full
SHA-1/SHA-256 object IDs, batched reads and per-request caches with explicit limits.

Expose capture/resolve/check/reanchor/view and literal source previews in both
hosts. UI capture updates the existing form and respects its native/managed save
owner. Whole-file/non-Git use and conservative file-level impact remain available.
Blob identity addresses immutable contents; review assesses lineage and meaning.

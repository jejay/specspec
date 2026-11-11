---
id: VnSF9BE=
type: requirement
parents:
- jsIUeP0=
---
# Define strict/expanding source tracking and explicit uncertainty

Implementation sources are either `{path, symbol?}` or `{path, symbol?, blob, mode,
ranges}` with all anchor fields present. Accept full lowercase 40/64-hex Git blob
IDs, mode strict/expanding, sorted non-overlapping positive inclusive [start,end]
pairs and canonical project-relative POSIX paths. Reject traversal, malformed
intervals, unsafe entry/path types and unsupported values with diagnostics.

Strict relocates surviving original lines and reports internal insertions or any
replacement/deletion touching the region as conflict. Expanding includes internal
insertions and wholly contained replacements, reporting modification as context.
Both exclude outer-boundary insertions and gaps between separate regions. Deletion,
ambiguous copies/moves, cross-boundary changes and missing objects remain explicit.

Resolve worktree text, exact index bytes or immutable commit files with node metadata
from the selected revision. Literal read-only previews identify target kind, mapped
ranges, mode and outcome; unreliable mapping shows original anchored contents.
Wrong object types, symlink/submodule entries, binary/LFS data, invalid UTF-8 and
exceeded budgets have visible uncertainty. Use bounded batched/cached Git reads,
diffs and mappings with external diff/textconv/lazy fetching disabled.

Capture defaults to HEAD, accepts explicit --staged and repeated --range START:END,
mode and symbol; preview is read-only. Capture/reanchor updates use the current
writer. Reanchor uses reliable mapped ranges or explicitly supplied conflict
replacement ranges. `check --staged --sources` evaluates exact staged graph/code and
retention; default staged checks evaluate graph structure. Region navigation supplies context
while source-change impact remains conservative per file.

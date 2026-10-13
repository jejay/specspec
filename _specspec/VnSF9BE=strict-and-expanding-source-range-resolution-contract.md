---
id: VnSF9BE=
type: requirement
parents:
- jsIUeP0=
---
## Current deletion correction

xu6W0c4=/5d5oDCM= supersede stored withdrawal, retired flags/controls and
format/API four with current-only format/API five. Withdraw by deleting the
Markdown file, keep reasons/earlier explanations in Git, and show HEAD-relative
deleted ghosts in the default workspace until commit. All earlier version/flag
workflow descriptions below are historical, not the current contract. Source
blob anchoring, no approval gates, native persistence distinctions and current-only
example-history policy remain; all retained Gantt revisions use actual deletions.

# Make tracking, lifecycle and verification behavior explicit

Call specific mode strict and broad mode expanding. A source object is either
whole-file {path,symbol?}, or additionally {blob,mode,ranges}; require all anchor
fields together, full lowercase 40/64-hex blob IDs, mode strict/expanding and sorted
nonoverlapping positive inclusive [start,end] pairs. Never store resolution states
as canonical approval/status fields. Retain canonical five-byte padded node IDs.

Strict relocates surviving original lines but reports conflict for insertion strictly
inside a region or any replacement/deletion touching it; inserted/replacement lines
are not absorbed. Expanding absorbs internal insertions and wholly-contained
replacements, while still reporting modification as review context. Insertions at
outer boundaries and gaps between separate ranges are excluded in both modes.
Deletion, duplicate/move ambiguity, cross-boundary replacement and missing history
remain explicit problems. Relocation is not proof of maintained implementation.

Targets are working file text, exact index bytes or immutable commit files; historical
metadata must be read from its selected revision, not current node records. Provide
literal read-only region previews for both hosts. Display target kind, mapped ranges,
mode and outcome; show original anchored content when mapping cannot be trusted.
Source path traversal/symlink escapes, submodules, symlink Git entries, wrong object
types, binary/LFS pointers, malformed UTF-8 and exceeded budgets must not silently
become valid line links. Use batched object reads/cached mappings and bounded diffs.

Capture defaults to HEAD or explicit --staged, supports multiple --range START:END,
mode and optional symbol; preview mode returns metadata without file writes. Ordinary
capture/reanchor are journaled canonical updates only. Reanchor is explicit: use
reliably resolved ranges or require supplied replacement ranges for conflicts.
Check outcomes are diagnostics, not structural node invalidation or approval.
Optional hook check --sources inspects ONLY staged graph and staged code, including
blob retention, without rewriting/staging/installing. Keep default graph hook behavior.

Keep whole-file source impact conservative; region navigation/tracing is not a
complete dependency analysis. Test insertion before/inside/between/at boundaries,
replacement/deletion, multiple ranges, copies/moves/renames, merge/branch and shallow
history behavior, SHA variants, exact index versus worktree, preview/native drafts,
retention and old-version rejection. Reconstruct and validate the entire Gantt
corpus, including withdrawn nodes, tags, real receipts and runnable stages; exercise
actual CLI and both hosts. Record actual failures/reruns and bounded uncertainty.

## Reproducible real-host verification environment

Use the supported reduced-motion preference for deterministic geometry/gesture
poses in the shared real-host harness. Keep normal-motion camera unit coverage
and production camera code unchanged; do not weaken pose, source, form or ink
assertions. The isolated Electron test launch disables background/occluded-window
timer throttling so intrinsic-resize observer work can complete predictably.
VS Code's aggregate shared/native smoke guards are 160 seconds each for the
expanded suite; individual CDP/request/watcher deadlines remain unchanged.
These are test-environment/budget choices, not universal timing/smoothness claims.
Record the earlier throttled camera/frame/source-preview failures and aggregate
shutdown failures as evidence; successful reruns do not erase uncertainty.

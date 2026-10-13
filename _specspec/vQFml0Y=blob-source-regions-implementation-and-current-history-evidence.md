---
id: vQFml0Y=
type: implementation
parents:
- VnSF9BE=
sources:
- path: src/specspec/source_schema.py
  blob: 28a84673073469bd31f455da908bcb50fd93af77
  mode: strict
  ranges:
  - - 1
    - 65
- path: src/specspec/sources.py
  blob: b00f5093dd1edc637e75d71f961651204d1e52a3
  mode: expanding
  ranges:
  - - 1
    - 443
- path: src/specspec/source_commands.py
  blob: d564a9e7646fb4b182193e66c818a8d1c714df3e
  mode: expanding
  ranges:
  - - 1
    - 220
- path: docs/source-regions.md
- path: electron/test-host/run.cjs
- path: example/gantt/history/cli.jsonl
- path: example/gantt/history/gantt.bundle
- path: example/gantt/history/revisions.json
- path: example/gantt/history/verify.py
- path: graph-ui-common/host/session.cjs
- path: graph-ui-common/media/graph-model.js
- path: graph-ui-common/media/graph.js
- path: graph-ui-common/test-host/ui.cjs
- path: graph-ui-common/test/graph.test.cjs
- path: graph-ui-common/test/session.test.cjs
- path: graph-ui-common/view.cjs
- path: src/specspec/cli.py
- path: src/specspec/editor.py
- path: src/specspec/format.py
- path: src/specspec/model.py
- path: tests/test_sources.py
- path: vscode/test-host/smoke.cjs
---
## Current deletion-only correction

xu6W0c4=/5d5oDCM= supersede the earlier retired/withdrawal workflow below.
Current schema/API 5 removes the flag and all retire/restore/filter/metadata/badge
paths. Managed delete physically unlinks an explicit batch after DAG checks,
with journal new=null and original-byte/recovery safeguards. Default HEAD-relative
UI ghosts are derived base records, read-only/copyable through staging and gone
after commit; Git HEAD/ref watching refreshes both hosts. Native Delete requires
clean project documents; deleted buffers never resurrect files in overlay reads.
All earlier workflow/schema/test counts below are historical evidence. Gantt's
entire current corpus is rebuilt with 22 physical deletions/reasons in prior Git
commits and a 22-node HEAD, no flagged retained nodes. Earlier root explanations
are in Git, not retained retired files. Source regions/colors/shapes/camera/native
Save remain in scope; the separate current implementation record links actual tests.

# Implement blob-addressed strict and expanding source hints in current-only format four

Implement v6xn2GU= through jsIUeP0=/VnSF9BE=. Keep original intentions, blob/lifecycle
choice and detailed mapping/testing rules separately addressable. Source schema is
now current-only format/API 4: whole-file hints still work, while text regions add
full SHA-1/SHA-256 blob, strict/expanding mode and sorted inclusive intervals.
No old API/schema reader, permanent migration, node fingerprint or approval gate.

source_schema shares validation between Markdown and CLI. SourceReader batch-checks
object type/size, batches bytes, caches listings/data/mappings and resolves paths
and ranges in worktree, exact index or commits. It excludes outer insertions/gaps,
reports strict internal edits and lets expanding absorb internal/contained edits.
Cross-boundary replacements, ambiguous copies/moves, deletion, wrong/missing blobs,
UTF-8/binary/LFS/entry/path/budget problems are explicit. Unique textual/contextual
moves and bounded Git rename evidence assist but do not prove code lineage or
meaning. Source Git reads disable lazy-fetch/external diff/textconv. Retention checks
recognize history/index tree edges, not hashes merely present in Markdown. File-level
impact stays conservative. No source data, object, index, ref or commit is auto-written.

CLI sources capture/resolve/check/reanchor/view supports source versions, multiple
regions, explicit index selection, preview/non-writing mode and deliberate replacement.
Ordinary capture/reanchor update only the canonical node through the existing writer.
Optional hook check --sources uses the exact staged graph/code and retention; default
hook remains graph-only. Whole-file/non-Git use remains available. Shared forms show
clickable anchored hints, resolve literal previews, identify original content on
untrustworthy mapping, and append capture metadata to the form rather than bypassing
VS Code native dirty documents or Electron managed saves. Historical capture is disabled.
No palette, type radii, geometry algorithm, camera logic or renderer-label persistence
change is introduced. Source controls add intrinsic form content, not fixed coordinates.

Converted the root manifesto through a one-time saved-byte/lock/stage/journal tool;
root IDs and ordinary files were unchanged by conversion. The first attempt caught
an accidentally removed PurePosixPath import before staging; restoring the import
allowed conversion. No permanent old-reader/converter shipped. Replayed all 123
maintained Gantt operations with current CLI, fresh consistent IDs, all eight refs,
withdrawn reasoning, new actual outputs, ledger/bundle/snapshot and staged source
anchors in each code pair. Strict model and expanding UI/helper references are
retained by those real synthetic code commits. All revisions validate with source
checks, actual context/impact, index, chronology and historical model suites.
First reconstruction failed the whitespace check from Windows text-pipe CRLF
conversion; byte stdin/LF writes fixed it. Next exposed a missing partial ledger
source during workflow add; writing the real evolving ledger before that operation
fixed it. Failed attempts remain outside this checkout. A combined rebuild/verifier
command hit the outer 300-second deadline after reconstruction had completed; an
unchanged standalone verifier passed. No maintained ref was left at an old schema.

Actual fresh evidence: 150 Python tests (30 focused sources), 135 common UI, 34 VS Code
adapter and nine Electron tests, Ruff, both validators, full current Gantt history/source
verifier and all three model stages; twenty final app-model tests and actual browser
in an external format-four clone; offline playground browser. Real Windows VS Code
shared/native and Electron suites passed including source preview and real stage
comparison. Source-preview screenshot inspected. This is bounded dispatched evidence,
not semantic tracking, production safety, remote CI, all themes/platforms or speed proof.

Record real-host failures, not just passes: default Electron runs intermittently failed
camera restoration, then hover visibility/intrinsic circular resize before frame work
completed. Shared geometry probes now use the existing reduced-motion branch; isolated
Electron test launches disable background/occluded timer throttling. No production
camera code or pose/ink/source assertion was changed. VS Code aggregate smoke guards
80/100 seconds expired as host exit caused CDP failures; they are now 160/160 for the
expanded suite, while individual request/CDP/watcher deadlines remain unchanged.
One source-preview run failed and later fresh-built runs passed; scheduling/stale assets
are not claimed as proven exclusive cause. A concurrent Python/Electron run passed the
entire shared UI but hit the existing desktop overall timeout during revision checks;
unchanged isolated Electron then passed. Diagnostic profiles/logs remain retained.

Existing default/earlier manual clones and experiments were not reset. Created a new
external gantt-source-regions clone for the format-four comparison/app checks; later
fixture reconstruction changes hashes, so the latest bundle is the maintained authority.
Agents should create a fresh external destination, not reset that clone. New production
commands do not install hooks or write Git. Spec commit precedes implementation commit;
stage final evidence/docs together and check exact index source links before committing.
Use this feature in its own implementation record: strict schema-policy and expanding
resolver/command module anchors captured from the committed implementation, plus
whole-file UI/test/corpus documentation references. Conclusions remain revisable.

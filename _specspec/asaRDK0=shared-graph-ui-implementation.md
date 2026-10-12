---
id: asaRDK0=
type: implementation
parents:
- V0xi_J8=
- YOPhqYc=
- mAZgRy8=
- fdB9ZLM=
sources:
- path: graph-ui-common/host/cli.cjs
  symbol: bounded shell-free API 4 invoke
- path: graph-ui-common/host/project.cjs
  symbol: nearest graph discovery
- path: graph-ui-common/host/session.cjs
  symbol: GraphSession
- path: graph-ui-common/media/graph-camera.js
  symbol: camera and native control exclusions
- path: graph-ui-common/media/graph-model.js
  symbol: metrics/layout/renderMatches
- path: graph-ui-common/media/graph.css
  symbol: semantic/Git-separated themed titles and corner letters
- path: graph-ui-common/media/graph.js
  symbol: host-neutral renderer and native drafts
- path: graph-ui-common/scripts/build.cjs
  symbol: buildGraph and dependency notices
- path: graph-ui-common/test-host/fixture.cjs
  symbol: real CLI/Git A/M/D only in disposable graph
- path: graph-ui-common/test-host/platform.cjs
  symbol: themed paint and desktop save/stale checks
- path: graph-ui-common/test-host/ui.cjs
  symbol: one real canvas harness for both hosts
- path: graph-ui-common/test/graph-model.test.cjs
  symbol: pure graph regressions
- path: graph-ui-common/test/graph.test.cjs
  symbol: native DOM/draft/hover/camera regressions
- path: graph-ui-common/test/session.test.cjs
  symbol: guarded host protocol
- path: graph-ui-common/view.cjs
  symbol: nonce-protected local template
- path: vscode/src/host.js
  symbol: project-scoped VS Code renderer adapter
---
# Extract one renderer and guarded graph session

graph-ui-common owns native DOM/SVG rendering, intrinsic layout/metrics, camera,
HTML/CSS, offline vendor/license build, bounded shell-free CLI and nearest-project
discovery. GraphSession unifies authorized API-2 reads/writes, history/legacy/stale
checks, confirmations and token/fingerprint/full-membership render acknowledgements.
Adapters supply posting/state, authorization, executable selection, native dialogs,
watchers and asset URLs. VS Code still hosts the editor surface at this extraction
checkpoint; its planned Activity Bar migration and Electron shell follow separately.
The renderer uses SpecSpecHost rather than importing/acquiring the VS Code API.
VS Code state is project-scoped and old single-project drafts remain recoverable.
Builds copy the common sources into self-contained host output, never fork renderer
sources; 12 dependency license notices remain bundled. All 68 common and 23 VS Code
regressions passed (the prior 85 plus six shared session tests), as did compilation.
The new tests cover stale/cancelled/legacy/history/authorization, exact modern
fingerprint acknowledgements, render timeouts/disposal, serialized reads/writes and
body-as-stdin rather than arbitrary renderer commands. This is not a completed
agent connector or proof of large-graph/platform/security perfection.


## Completed first host-adapter slice

VS Code and Electron now build identical shared graph.js/model/camera/CSS/template/
session assets. Host ports remain small: no VS Code or Electron imports in the
renderer, no schema/hash mutation forks. Shared text-only Git corners/titles read
host theme tokens, keep R/source/withdrawal distinctions, and don't change semantic
fills or canonical data. Non-disabling progress notices make slow CLI/Git reads
visible without losing native drafts. Project-scoped state is the adapters' contract.
All 72 common tests passed, including four Git cue/draft/CSS regressions beyond the
68-test extraction checkpoint. The common real Chromium harness checks both Windows
hosts on disposable CLI/Git fixtures: geometry/metrics/hover, native forms/cameras,
computed A/M/D paint and live theme variables. It accounts for base-only metric
contexts and visible hover targets without excluding other edges from clearance
checks. Electron-specific real save/stale/reload/history checks use the same harness.
Tests are dispatched evidence, not full manual or Linux/performance certification.


## Hash-free Markdown synchronization revision

The later manual-edit intention and separate hash-free/watcher conclusion supersede
all earlier API-2/fingerprint/stale-hash claims in this record. Current code uses
API/format 3, no managed_hash or fingerprint gate, and permits valid manual edits.
Original detailed test counts and packaged-host evidence above remain historical,
not claims of re-running every old package or platform against this revision.

GraphSession coalesces watcher events, retries failed reads twice, compares records
directly and validates current files before UI writes. Render sequence/full-membership
checks remain without fingerprint acknowledgements. Dirty drafts retain original
node records/caret/camera; unrelated changes permit saving, same-node overwrites ask
confirmation, and deletion/invalid files preserve copyable drafts. Invalid reloads
mark the last valid graph out of date and disable mutations until a valid reload.
VS Code watches directory/files; Electron's shared GraphWatcher also watches the
parent and reattaches after canonical-directory recreation. Optional configurable
polling defaults to zero/off and is disposed with sessions. No silent fallback,
universal event-delivery guarantee or adversarial race-free writes are claimed.

The independent Gantt working graph was migrated without changing body/relationship
semantics. Its original CLI receipts/Git commits are retained verbatim. The history
verifier now reconstructs records and compares actual contents directly; archived
hash strings are opaque receipt labels, not a current hash algorithm or edit gate.
See the separate current implementation record for source links and final checks.


## Installed VS Code recheck before the authorized commit

The user requested another real VS Code run after the earlier executable-update
block. All 29 editor adapter tests and the installed Windows host smoke now pass,
including complete 69-node target/70-node display rendering, watcher-only manual
Markdown synchronization, deliberate invalid-file diagnostics/recovery without
rewriting those files, and preserved drafts/caret/camera/native controls. Both real
working graphs are valid with warnings as errors; deliberately malformed fixtures
are disposable and restored. No Linux/macOS or remote-CI run is inferred. See the
hash-free-markdown-sync implementation record for the current complete evidence.

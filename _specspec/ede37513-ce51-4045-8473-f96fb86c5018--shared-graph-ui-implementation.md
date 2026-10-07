---
id: ede37513-ce51-4045-8473-f96fb86c5018
type: implementation
parents:
- 2b6a0e4e-f07f-4932-b58b-40348d4c3ac1
- 65f28474-18be-46f8-89f6-b9ce30a0ec96
- d70cdad5-5e03-4200-ac75-74cf6514e56c
- 037c4383-1934-4181-96e5-9fc3b2958e2f
sources:
- path: graph-ui-common/host/cli.cjs
  symbol: bounded shell-free API 2 invoke
- path: graph-ui-common/host/project.cjs
  symbol: nearest graph discovery
- path: graph-ui-common/host/session.cjs
  symbol: GraphSession
- path: graph-ui-common/media/graph-camera.js
  symbol: camera and native control exclusions
- path: graph-ui-common/media/graph-model.js
  symbol: metrics/layout/renderMatches
- path: graph-ui-common/media/graph.js
  symbol: host-neutral renderer and native drafts
- path: graph-ui-common/scripts/build.cjs
  symbol: buildGraph and dependency notices
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
- path: graph-ui-common/test-host/ui.cjs
  symbol: one real canvas harness for both hosts
- path: graph-ui-common/test-host/fixture.cjs
  symbol: real CLI/Git A/M/D only in disposable graph
- path: graph-ui-common/test-host/platform.cjs
  symbol: themed paint and desktop save/stale checks
- path: graph-ui-common/media/graph.css
  symbol: semantic/Git-separated themed titles and corner letters
managed_hash: 6735ef519b07ef01f19b602b89cc6c4086e1821e6eeb096a39a99842f7144965
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

---
id: ede37513-ce51-4045-8473-f96fb86c5018
type: implementation
parents:
- 65f28474-18be-46f8-89f6-b9ce30a0ec96
- 2b6a0e4e-f07f-4932-b58b-40348d4c3ac1
- d70cdad5-5e03-4200-ac75-74cf6514e56c
sources:
- path: graph-ui-common/media/graph.js
  symbol: host-neutral renderer and native drafts
- path: graph-ui-common/media/graph-model.js
  symbol: metrics/layout/renderMatches
- path: graph-ui-common/media/graph-camera.js
  symbol: camera and native control exclusions
- path: graph-ui-common/view.cjs
  symbol: nonce-protected local template
- path: graph-ui-common/host/session.cjs
  symbol: GraphSession
- path: graph-ui-common/host/cli.cjs
  symbol: bounded shell-free API 2 invoke
- path: graph-ui-common/host/project.cjs
  symbol: nearest graph discovery
- path: graph-ui-common/scripts/build.cjs
  symbol: buildGraph and dependency notices
- path: graph-ui-common/test/session.test.cjs
  symbol: guarded host protocol
- path: graph-ui-common/test/graph.test.cjs
  symbol: native DOM/draft/hover/camera regressions
- path: graph-ui-common/test/graph-model.test.cjs
  symbol: pure graph regressions
- path: vscode/src/host.js
  symbol: project-scoped VS Code renderer adapter
managed_hash: 8fad93c6c760ad5ac84c57ff21b00d685c97f8a977d126f7c5f9913d187b6a04
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

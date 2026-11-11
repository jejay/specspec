---
id: BbLribU=
type: implementation
parents:
- 6MUwTIw=
sources:
- path: electron/test-host/run.cjs
- path: graph-ui-common/media/graph-model.js
- path: graph-ui-common/media/graph.css
- path: graph-ui-common/media/graph.js
- path: graph-ui-common/test-host/ui.cjs
- path: graph-ui-common/test/graph-model.test.cjs
- path: graph-ui-common/test/graph.test.cjs
- path: vscode/test-host/run.cjs
---
# Paint immediate hover context and darken its surroundings

`updateHoverAppearance` builds the direct displayed-neighbor set from incident
edges, toggles existing card/pair classes and raises incident pairs. CSS applies
brightness(.45) to unrelated cards and 35% ink / 65% black to non-incident links.
The same membership logic handles gray roots, history, reversed and draft edges.

Delegated hover state, hit reconciliation and exit restoration preserve native
forms, world positions, camera, curve/head geometry and pair ordering. Model/DOM
and actual-host paint checks cover exact membership, isolated/expanded cases,
stationary-pointer refresh, same-identity redraw and restoration.

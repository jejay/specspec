---
id: YHSK9DA=
type: implementation
parents:
- AZbsoEA=
sources:
- path: graph-ui-common/media/graph.css
- path: graph-ui-common/media/graph.js
- path: graph-ui-common/media/graph-model.js
- path: graph-ui-common/test/graph-model.test.cjs
- path: graph-ui-common/test/graph.test.cjs
- path: graph-ui-common/test-host/ui.cjs
- path: tools/rainbow-playground/index.html
- path: graph-ui-common/test/playground.test.cjs
- path: graph-ui-common/test-host/playground.cjs
- path: docs/node-canvas.md
- path: docs/own-spec.md
---
# Render square implementations, rounder requirements and circular roots

Shared CSS has Implementation 0px, Requirement 24px and manifesto 50% radii in
compact/expanded states. Ordinary cards are 264×112/860-expanded; compact root is
264×264. `applyLayout` measures the same native form at 822px content width and
uses `manifestoDiameter = ceil(hypot(width,height)+48)` for its expanded circle.
Intrinsic resize updates the footprint while preserving editor/caret/camera.

`sideBoundary` and `routeEdges` attach to actual outlines with 3-unit clearance,
middle-40% circle chords, full-height ordinary ports and clear straight leads.
Conservative boxes supply corridors. The playground root sample is a 150px circle.

Pure/DOM/actual-host tests check type radii, formula/content/Git-marker fit, measured
grow/shrink, reverse routes, painted clearance and native fields. Independent
collision checks explicitly handle zero-radius square interiors and actual circles.
Palette, label state and logical relationships retain their own contracts.

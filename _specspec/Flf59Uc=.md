---
id: Flf59Uc=
type: implementation
parents:
- 6QB9hRY=
sources:
- path: graph-ui-common/media/graph-model.js
- path: graph-ui-common/media/graph.js
- path: graph-ui-common/media/graph.css
- path: graph-ui-common/view.cjs
- path: graph-ui-common/test/rainbow.test.cjs
- path: graph-ui-common/test/graph.test.cjs
- path: graph-ui-common/test-host/platform.cjs
- path: graph-ui-common/test-host/ui.cjs
- path: docs/own-spec.md
- path: tools/rainbow-playground/palette.js
- path: tools/rainbow-playground/index.html
- path: tools/rainbow-playground/README.md
- path: graph-ui-common/test/playground.test.cjs
- path: graph-ui-common/test-host/playground.cjs
---
# Render exact seven-color and comparison-role fills

`graph-model.js` exports the exact selected `RAINBOW_COLORS`, neutral/type/revision
maps, labels and modes. Requirement is index 4 and Added 3; Implementation 0,
M/R 1, D 6 and source-only 5. Distance uses `(d-1)%7`; unknown/neutral is gray.
The renderer derives revision kinds from the selected comparison before source
impact and applies them equally to compact/expanded/root cards.

The local template persists mode preferences and renders accurate legends. Native
forms/caret, camera/geometry and independent Git title/edge cues survive mode changes.
Tests compare literal bytes/mappings, independently converted OKLCH, cycle wrap,
root/type/status/no-comparison/draft behavior and exact playground default exports.

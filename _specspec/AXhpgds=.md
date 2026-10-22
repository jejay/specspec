---
id: AXhpgds=
type: implementation
parents:
- xCOHepQ=
sources:
- path: graph-ui-common/media/graph.css
- path: graph-ui-common/media/graph-model.js
- path: graph-ui-common/media/graph.js
- path: graph-ui-common/test/graph.test.cjs
- path: graph-ui-common/test-host/ui.cjs
- path: graph-ui-common/test-host/platform.cjs
- path: vscode/test-host/run.cjs
- path: electron/test-host/run.cjs
---
# Paint shared tints and fit readable editor and Git information

Shared CSS uses ordinary theme text, 15% resting/24% hovered accent tints and shared
contrast-theme rules. Neutral distance/type roots keep `#d3d3d3`; colored hover
borders use the hue emphasis contract. Expanded ordinary cards are 860 wide and
the native textarea/revision text keeps an 822px content budget with host monospace
font/size. Typical 80-column ASCII fitting is checked at 13/14/16px.

Git letters are 20px/800 weight with bottom-right anchoring and badge clearance.
Actual-host tests check compact content/corner fit, circular marker placement,
editor/pre width, tint/hover restoration, native DOM/caret and unchanged geometry.

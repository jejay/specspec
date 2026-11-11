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
# Paint the shared tints and fit the editor and the Git letters into the cards

`graph-ui-common/media/graph.css` gives every card the ordinary text color of the theme, a tint of 15% of its accent at rest and 24% on hover, and one rule for the high-contrast themes. A manifesto of the distance and type modes has the accent `#d3d3d3`. On the light themes of VS Code its border at rest is `#767676`, which has a contrast of 4.3:1 against the tint. The border of a hovered colored card is emphasized in its hue. An expanded card of a requirement or an implementation is 860 wide, and the inline editor of the node text has 822px for its content, uses the monospace font and font size of the editor it runs in and has room for its gutters of line numbers and change marks. Tests check that a typical line of 80 ASCII columns fits at 13, 14 and 16px.

The Git letters are 20px high with weight 800, anchored at the bottom right, and the badges keep clear of them. The tests in the installed VS Code and desktop app check that the content and the corner letter of a compact card fit, that the letter of a round manifesto is placed inside it, the width of the inline editor, that tint and hover paint are restored, and that the DOM of the form, the text cursor and the geometry are the same afterwards.

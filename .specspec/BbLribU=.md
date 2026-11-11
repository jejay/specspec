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
# Paint the direct relationships of the hovered card and darken everything else

`updateHoverAppearance` in `graph-ui-common/media/graph.js` collects the hovered card and the endpoints of the links drawn to or from it. It toggles the class `incident-highlight` on the existing pairs of curve and arrowhead that touch the hovered card and the class `hover-darkened` on every other pair and on the unrelated cards, and it appends the incident pairs last, which raises them above the others. `graph.css` darkens an unrelated card with `brightness(.45)` and a link that is not incident with 35% of its ink and 65% black. The gray manifesto, the links of an earlier revision, links drawn against the direction of the layout and draft links go through the same rule of membership.

`trackHover`, `syncHover` and `clearHover` keep the hover state from events delegated to the viewport, test again after a redraw or a camera movement which card is under the pointer, and restore the paint when the hover ends. The form, the positions in the world, the camera, the geometry of curves and arrowheads and the order of the pairs are the same before, during and after a hover. The tests of the model and of the DOM in `graph-ui-common/test` and the paint checks in the installed VS Code and desktop app cover the exact membership, an isolated card, an expanded card, a refresh under a pointer that does not move, a redraw with the same hovered card and the restoration.

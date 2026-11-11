---
id: JTezmL0=
type: implementation
parents:
- E7O_6GU=
- rvz48KY=
- RY5LFw8=
sources:
- path: graph-ui-common/media/graph-model.js
  blob: 7e9e35d891231a16e72a356cb83b32dc5f456cf0
  mode: strict
  ranges:
  - - 231
    - 231
  - - 325
    - 333
  - - 345
    - 354
- path: electron/main.cjs
- path: electron/security.cjs
- path: electron/test-host/run.cjs
- path: electron/test/security.test.cjs
- path: graph-ui-common/host/annotations.cjs
- path: graph-ui-common/host/session.cjs
- path: graph-ui-common/media/graph-annotations.js
- path: graph-ui-common/media/graph.css
- path: graph-ui-common/media/graph.js
- path: graph-ui-common/test-host/platform.cjs
- path: graph-ui-common/test-host/ui.cjs
- path: graph-ui-common/test/annotations.test.cjs
- path: graph-ui-common/test/graph.test.cjs
- path: graph-ui-common/test/session.test.cjs
- path: graph-ui-common/view.cjs
- path: vscode/src/extension.ts
- path: vscode/test/extension.test.cjs
- path: graph-ui-common/test-host/canvas.cjs
---
# Paint highlight rings by node ID and switch to the comparison of a selected spotlight

The shared renderer paints the rings set by hand and the rings applied from a spotlight with the one CSS variable `--spotlight-color` in `graph.css`: white by default and black on the light and the high-contrast light theme of VS Code, with a contrast of at least 4.5:1 against every card tint. `graph-annotations.js` toggles an ID on Shift-click and removes it on a click with Ctrl or Command and Shift. `annotationRingWidth` in `graph-model.js` gives the ring the width `max(5, 3 / k)`, and the negative offset keeps it inside the card at every camera scale, apart from the paint of focus, of the fill and of Git marks. A modal dialog for the message captures the IDs and the comparison on display through the shared session, which checks authorization.

The dropdown lists the newest spotlight first. It shows badges for arrivals, closes on Escape or on a click or focus outside and stays inside the window. Selecting a record hands the switch of the comparison to the shared session in `session.cjs`. All IDs are applied, and the available nodes are framed only once the comparison is displayed. A deleted node of the base and a version of the working files that drifted can be highlighted, and an ID without a card stays selected. Warnings about the working files are visible outside the menu. Drafts, the inputs of the form and the camera are the same after an arrival and after a creation. Navigating explicitly to another comparison releases the active spotlight and keeps the editable IDs.

The tests of the shared renderer and session and of the two adapters cover toggling, clearing and composing with one ink, the switch of the comparison before the framing, highlights under drift and with missing members, warnings about a moved HEAD, arrivals and their baselines, comparisons between commits, authorization, errors and the reviewed flush. The checks in the installed editors drive the command line, whose arguments name no colors, and exchange spotlights as metadata in both directions. They hold for the platforms and file systems they ran on, and the Command key of a physical Mac lies outside what they cover.

On Windows the checks in both installed editors cover a live drift warning with rings that persist, the selection of a historical comparison with nodes that were really added and deleted, drafts of forms that stay, an agent reading back metadata alone, and the baselines after a reload. The paint checks use the fill schedule between 40% and 16% of camera scale and the ring sizes scaled by the camera.

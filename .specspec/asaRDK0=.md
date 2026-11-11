---
id: asaRDK0=
type: implementation
parents:
- V0xi_J8=
- FHfnj08=
- 3jX0Rgk=
- NsFLK9o=
- fdB9ZLM=
- eqWEPJI=
- zwevPEc=
sources:
- path: graph-ui-common/host/cli.cjs
- path: graph-ui-common/host/project.cjs
- path: graph-ui-common/host/session.cjs
- path: graph-ui-common/media/graph-camera.js
- path: graph-ui-common/media/graph-model.js
- path: graph-ui-common/media/graph.css
- path: graph-ui-common/media/graph.js
- path: graph-ui-common/scripts/build.cjs
- path: graph-ui-common/test-host/fixture.cjs
- path: graph-ui-common/test-host/platform.cjs
- path: graph-ui-common/test-host/ui.cjs
- path: graph-ui-common/test/graph-model.test.cjs
- path: graph-ui-common/test/graph.test.cjs
- path: graph-ui-common/test/session.test.cjs
- path: graph-ui-common/view.cjs
- path: vscode/src/host.js
- path: graph-ui-common/src/graph-vendor.js
- path: graph-ui-common/test/host-ui.test.cjs
- path: graph-ui-common/test/camera.test.cjs
- path: graph-ui-common/test-host/canvas.cjs
---
# Render the graph, its layout and its camera in the code that both graph editors share

`graph-ui-common` holds the canvas that both graph editors share. `graph-ui-common/view.cjs` is the HTML template, `graph-ui-common/media/graph.js` renders the cards as DOM elements and the links as SVG, `graph-ui-common/media/graph-model.js` holds the pure functions for the metrics of a revision, the layout and the routing, and `graph-ui-common/media/graph-camera.js` is the camera. `graph-ui-common/host/cli.cjs` runs the command line within limits of 120 seconds and 16 MiB of output, `graph-ui-common/host/project.cjs` finds the project directory, and `GraphSession` in `graph-ui-common/host/session.cjs` guards every operation.

In `graph-model.js`, `metrics` computes for each revision the shortest and the longest distance of a node from the manifesto and the number of its unique descendants. `layoutBackbone` ranks every node after all its parents and picks the forest for the placement deterministically, `layoutGraph` hands that forest to Dagre, and `routeEdges` leads every drawn link through clear corridors to ports on the actual outlines of its cards. In `graph.js`, `draw` moves the one form element into the expanded card of the selected node, `compactCard` writes the downstream count onto each child, and `gitCorner` adds the letter A, M or D with its accessible label. `graph-ui-common/media/graph.css` colors the headline and the letter of a changed node from the Git variables of the theme, with defaults for a standalone window, and sets no `will-change` on the graph. A camera update adjusts the paint of links and cards, and the form elements and the positions in the world stay as they are.

The interface between the renderer and its editor keeps state and messages apart for each project and each view, and `vscode/src/host.js` is its adapter in VS Code. The session carries out the authorized operations one after another and matches the sequence number and the list of shown nodes with which the renderer acknowledges each rendering. An adapter supplies what only its editor can provide. `graph-ui-common/scripts/build.cjs` copies the common files into the build of each editor and bundles the libraries that `graph-ui-common/src/graph-vendor.js` names, in pinned versions that work offline, together with their license notices.

The tests of the pure model in `graph-ui-common/test/graph-model.test.cjs`, of the DOM in `graph-ui-common/test/graph.test.cjs` and of the session in `graph-ui-common/test/session.test.cjs`, together with one harness for the installed editors, check which nodes a view shows, that the values of two revisions stay apart, the paint at low zoom, the focus, the drafts and the text cursor, the camera and the clearance of the drawn links. The harness consists of `graph-ui-common/test-host/ui.cjs` and `graph-ui-common/test-host/platform.cjs` and works on a disposable checkout of the history of the Gantt example, which `graph-ui-common/test-host/fixture.cjs` prepares.

`neutralEdgeStrength` in `graph-model.js` gives the ink of ordinary links a strength between 70% and 35%, and `updateCameraAppearance` in `graph.js` passes it on as the CSS property `--normal-edge-strength`. The sizes of lines and arrowheads and the separate paint of comparisons and of hover are independent of it. Unit tests check the function, DOM tests check that a camera change reaches the property, and probes in the installed editors read the computed colors of curves and arrowheads at actual size, at an intermediate zoom and at the smallest zoom.

The harness drives the installed editors through the Chrome DevTools Protocol. `foreground` in `ui.cjs` maximizes the window where the editor supports that and brings it to the front in either case. The `CDP` client rejects every pending request at once when the connection closes or fails and clears the timers of these requests. A protocol error, a JavaScript exception and the timeout of a single request each count as a failure. `graph-ui-common/test/host-ui.test.cjs` exercises these cases with a stand-in for the socket, without a browser.

`createCamera` in `graph-camera.js` owns the one-shot rectangle tool: it arms on hover with Ctrl or Command held, keeps a drag of the primary pointer going after the modifier is released, draws the band in the coordinates of the viewport, converts it through the camera of the start with `rectangleBounds`, consumes the click after the release and cleans up after a cancellation and on disposal. The floating rounded control in `view.cjs` holds the icons for framing the graph, the selected node when there is one, and a rectangle. The controls of the form and the Shift gestures for highlights receive their events as they do without the tool. `frameTransform` lets a rectangle zoom in to 250% and caps the framing of the graph and of a node at 100%.

`nodeFillStrength` drives one inherited CSS property, `--node-fill-strength`, with which `graph.css` mixes each exact tint of actual size toward the painted border, in two stages in sRGB. The fill changes between scales of 40% and 16%, and the ink of ordinary links changes between 70% and 16%, from a strength of 70% to 35%. `graph-ui-common/test/camera.test.cjs` covers both scale functions with their end points, every direction of a drag, the release of the modifier, the pointer capture, cancellation, presses on form controls, positions and text cursor that stay as they are, and the Mac mapping with synthetic events. DOM tests verify the two different onsets and that a camera change reaches both properties. `graph-ui-common/test-host/canvas.cjs` runs first in each installed editor and checks the fills of dark, light and high-contrast themes at three scales, a real pointer capture with a release outside the canvas, the icons that depend on the context, and editing. The complete suites in the installed editors combine these probes with the checks of sources, of spotlights, of the lifecycle of VS Code documents, of recovery after watcher events and of stored state across reloads and revisions.

Each add, save and delete carries a `requestId`, and its form stays pending until a `completed`, `error` or `cancelled` reply with that ID arrives. An `applied` message closes the form of a created node before the refresh that follows, so that the node cannot be submitted twice. A prompt about unsaved changes is a bar inside the page with the role `alertdialog` and the buttons Keep editing, which has the focus, and Discard changes, in both graph editors. A redraw gives the focus back to the card with the same node ID, and the cards follow the order of the layout for tabbing, by rank and then by vertical position. The renderer tests cover a queued add whose refresh fails, the keyboard behavior of the confirmation bar, the restoration of focus and the tab order.

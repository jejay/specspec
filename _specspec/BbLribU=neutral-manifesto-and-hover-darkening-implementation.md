---
id: BbLribU=
type: implementation
parents:
- 6MUwTIw=
sources:
- path: graph-ui-common/media/graph-model.js
  symbol: TYPE_COLORS, color
- path: graph-ui-common/media/graph.js
  symbol: drawLegend, updateHoverAppearance, drawEdges, syncHover
- path: graph-ui-common/media/graph.css
  symbol: manifesto fill/text and hover-darkened card/curve/head paint
- path: graph-ui-common/test/graph-model.test.cjs
  symbol: fixed manifesto color regression
- path: graph-ui-common/test/graph.test.cjs
  symbol: darkening membership, redraw, forms, history, drafts and legends
- path: graph-ui-common/test-host/ui.cjs
  symbol: checkHover paint and root dark/light/contrast CSS probes
- path: vscode/test-host/run.cjs
  symbol: maintained Gantt and native document verification
- path: electron/test-host/run.cjs
  symbol: shared canvas and desktop persistence/revisions
---
## User correction after this implementation

The solid gray root/dark text described below was an incorrect interpretation
of light gray. iktVTRU= clarifies shared tinted-card styling with a white hover
border; xCOHepQ= chooses its replacement. Prior checks/screenshots are actual
earlier evidence, not approval of that appearance or current solid-fill behavior.
The neutral root accent/legend and one-hop darkening remain implemented.

# Render a neutral manifesto and darken outside hovered relationships

Study the original intention/design documents, own-spec tour and UI/root/color/
arrow/hover/camera/shared-host conclusions with their ancestors before implementation.
The existing renderer already emphasized immediate incoming/outgoing SVG pairs.
Implement the user's two additions in that single source, not in separate host
renderers, domain metadata or a backend mutation path.

color returns #d3d3d3 for manifesto nodes before choosing distance/type palettes.
Compact and expanded roots share a solid gray background (also under hover and
high-contrast classes), dark ordinary text and light badge backing. Native inputs,
Git title/corner colors, comparison text and focus/borders keep their own styling.
Distance legends give the manifesto its own gray zero-hop swatch rather than
claiming the generic distance-zero blue. Type legends use the same neutral color.
Non-root palettes, snapshot metrics and world arrangement remain unchanged.

updateHoverAppearance replaces updateEdgeHighlights. Build one direct-neighbor
set from incident drawn edges, keeping the hovered card itself even when isolated.
Toggle hover-darkened on every other existing card and non-incident curve/head
pair; retain incident-highlight and pair paint ordering. CSS uses brightness(.45)
on unrelated cards and 35% ink/65% black for unrelated connections, preserving
Git hue/dashes and all path/head geometry. The root also dims if unrelated. Links
between neighbors still dim unless incident to the hovered card. Historical,
reversed and unsaved draft links count when drawn. Redraw reapplies classes even
when hovered identity is unchanged; existing pointer/camera hit reconciliation
and exit/blur/cancel/touch clearing remain. Forms/caret/drafts/host state are not
recreated or mutated by hovering. SVG remains non-interactive.

Six added shared model/DOM regressions plus strengthened existing hover assertions
cover fixed colors/legends, exact one-hop membership and neighbor-to-neighbor links,
unrelated gray root, isolated cards, historical/reversed/draft links, expanded
native forms, unchanged draft/DOM identity/messages/caret, same-identity redraw,
stationary-pointer camera changes, disappearance and clearing. The shared real-host
suite now asserts actual darker non-incident stroke/head channels, paired classes,
card brightness and restoration, unchanged geometry/order/cameras, all color modes
and dark/light/high-contrast CSS probes. No assertion or timeout was weakened.

Local Windows checks passed: 105 shared UI tests, 34 VS Code tests, nine Electron
tests, 100 Python tests, Ruff lint/format and both working graphs with warnings as
errors. Complete installed VS Code and Electron host suites passed separately on
the maintained 44-node target/45-node display Gantt fixtures. VS Code also passed
native dirty/save/undo/redo, split documents/cameras and raw invalid-buffer repair;
Electron passed real saves, watcher/draft reload and revision switching. Initial
concurrent runs alongside full pytest timed out in CDP/host waits; isolated reruns
passed without code/test-limit changes. That suggests load sensitivity, not a
proved root cause. A further full Electron run with screenshots also passed.
Inspected overview hover, light-theme probe and expanded-root screenshots show
visible context darkening and the gray root; ignored local logs/screenshots are
not canonical graph files or committed test artifacts.

Update README, conclusion context, graph tour and older hover/fill/editor records,
including the renamed helper's source reference, without rewriting the user's
parent intentions. Specification-first and implementation commits are explicitly
user-authorized; validate complete exact staged graphs before each. No hooks are
installed and unrelated untracked settings/emblem files remain untouched.

This is bounded Windows/browser evidence, not remote CI, other-platform host,
full accessibility, optimal rasterization under transient filters or large-graph
performance certification. The light/dark/contrast probes change CSS in isolated
hosts, not a claim of testing every installed theme. Constants remain revisable;
passing tests and commits do not establish approval or universal correctness.

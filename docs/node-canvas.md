# Node-canvas implementation rationale

This is noncanonical design/evidence context. The [graph tour](own-spec.md#blender-style-canvas-revision)
links the accepted user intentions and separately proposed technical conclusions.
Working code does not accept a proposal. `INTENTION_SPEC.md` is unchanged.

## Reuse rather than a Blender port

Reviewed upstream descriptions/APIs:

| Candidate | Fit and trade-off |
| --- | --- |
| [React Flow](https://reactflow.dev/) | MIT, mature node UI with pan/zoom and custom React nodes. Good future option, but adopting it here would replace the existing native form/state layer with React. |
| [Rete](https://retejs.org/docs/) | Modular editor with rendering plugins and computational dataflow/control-flow engines. More abstraction than this specification viewer currently needs. |
| [LiteGraph](https://github.com/jagenjo/litegraph.js) | Canvas-based editor resembling visual programming tools, with navigation and executable graphs. Its Canvas widgets/execution model are not a substitute for safe native Markdown/JSON editing. |
| [ELK.js](https://github.com/kieler/elkjs) | Powerful layered/port routing, async worker support. A credible alternative, but heavier integration/license footprint than the current synchronous medium-graph slice. |
| [Dagre](https://github.com/dagrejs/dagre/wiki) | MIT, rendering-independent directed layout from node sizes and relationships. Fits the existing DOM/SVG renderer without changing the canonical backend. |
| [D3 zoom](https://d3js.org/d3-zoom), [D3 shape](https://d3js.org/d3-shape/curve) | ISC, established DOM/SVG navigation and Bézier generation. Reuse the gesture/transition behavior rather than implementing a new pan/zoom engine. |

Chosen proposal: **Dagre + focused D3 modules**, bundled offline with esbuild. This
is a Blender-inspired interaction surface, not a JavaScript port of Blender,
shader engine, socket type system, freely draggable dependency editor, or brand copy.

## Separation of responsibilities

- **Python** validates schemas, lifecycle, links, fingerprints, and writes.
- **Dagre** lays out stable ordered IDs/relations in LR mode. Its inputs contain
  intrinsic card sizes, spacing, and graph relationships; no viewport size.
- **D3 shape** creates smooth right-to-left socket connections. Long edges retain
  flat reserved lanes across skipped card-width bands before curving through gaps.
  Direct links use horizontally tangent Béziers. Old reverse relationships use
  an outer loop; a revision union is a presentation graph, not a valid canonical DAG.
- **D3 zoom** applies one transform to cards and SVG. The viewport clips overflow;
  panning is unconstrained and scale is 12–250%. Wheel/pinch anchoring and drag
  event handling come from the library. Framing/zoom buttons animate except under
  reduced-motion preferences. Resizing does not refit or reflow the graph.
- **Native forms** retain text editing, selection, scrolling, resize, keyboard
  controls, drafts, and original stale-context fingerprints. Camera gestures are
  excluded from settings controls. Navigation alone sends no mutation commands.
- **Webview state** holds overview/per-node camera preferences and drafts. No
  layout positions, magnification, colors, or derived scores enter `_specspec`.

## Build, licenses, and packaging

`npm --prefix vscode ci` then `npm --prefix vscode run compile` builds
`vscode/media/vendor/graph-vendor.js` from `vscode/src/graph-vendor.js` and generates
`THIRD_PARTY_NOTICES.txt` containing licenses for every bundled dependency.
Build artifacts are ignored in Git but included in extension packaging. Node
modules and build sources are excluded from the VSIX. The lockfile pins versions.
There are no CDN/runtime network requests, `eval`, or executable project Markdown.

## Verification and boundaries

Node tests cover left-to-right constraints, deterministic ordering, skipped-rank
routing, historical overlays, pointer-anchored zoom, zoom bounds, viewport-size
invariance, independent cameras, native-control exclusions, keyboard navigation,
form caret preservation, and the earlier editor/bridge/trust regressions.

`npm --prefix vscode run test:host` opens installed VS Code in a disposable profile.
Chromium checks the real graph, focuses nodes, pans/zooms, narrows the canvas,
resizes a textarea, samples curves for card/content intersections, checks side-port
endpoints, restores the overview camera, and switches semantic colors. Optional
`SPECSPEC_SCREENSHOT_DIR` captures screenshots of overview and focused views. The
agent inspected these on Windows; this does not replace full human editing/review
or revision-picker verification. Only this isolated automated test disables trust.

The current layout is synchronous and renders all nodes. Large-graph virtualization,
manual node dragging/reparenting, minimaps, configurable Blender keymaps, and
language-resolved source navigation remain out of scope. Crossing reduction is a
layout heuristic, not a guarantee of an optimal diagram for every possible graph.

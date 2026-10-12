# Node-canvas implementation rationale

This is noncanonical design/evidence context. The [graph tour](own-spec.md#blender-style-canvas-revision)
links the user's intentions and separately reasoned, revisable technical conclusions.
Review is risk-proportionate rather than a per-node approval workflow; implementation
is evidence, not permanence or correctness. `INTENTION_SPEC.md` is unchanged.

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

- **Python** validates schemas, withdrawal, links, and writes.
- **Dagre** produces a left-to-right presentation from stable ordered IDs,
  intrinsic sizes, and relationships; no viewport size. Reversed input and its
  RL longest-path ranker produce **earliest source ranks**, rather than drawing
  shallow branches toward a shared sink. Compute ranks from **all parents**, then
  place a deterministic deepest-parent backbone to prevent vertical stretching by
  common sinks. All relationships are still drawn; the backbone is not canonical
  or a preferred/approved dependency. Each node follows its deepest parent;
  this is deliberately not the shortest-hop context metric. Target edges rank
  the overview/current focus; base edges rank a removed selected node's context.
  Extra revision references into primary nodes are overlays, not rank constraints.
- **D3 shape** connects parent right boundaries to child left boundaries, without
  circles. Long edges retain flat reserved lanes across skipped card-width bands.
  Attachments span intrinsic card heights instead of a narrow title band. A short
  horizontal departure prevents steep thickened curves from brushing the source;
  a tangent-aligned settling approach precedes the arrow. The line ends at its
  filled head's base, not through the tip. Forward non-backbone links choose the
  nearest clear gaps across skipped columns, remaining flat through each column;
  outer corridors are fallback lanes. Reverse historical links use an outer loop.
- **Edge appearance** compensates for camera scale: minimum stroke strength is
  1.6 CSS screen pixels, minimum head length is 6, and Git dash lengths remain
  visible. The fixed world-space settling approach accommodates the largest head
  at the current 12% camera limit. These are implementation choices, not canonical
  node metadata or fixed user pixel requirements. No edge/form DOM is recreated
  and no layout or mutation runs during zoom.
- **Distance fills** select shortest (minimum/default) or longest (maximum)
  directed edge counts from the manifesto, computed iteratively across each full
  snapshot. Cycles/blocked descendants have no finite maximum. Surviving/removed
  nodes use target/base metrics respectively, not the revision union or placement
  backbone. Legends explain the selected metric; on-node hop labels are removed.
  Downstream, Git, and withdrawn badges remain independent.
- **Compact spacing** uses 112-unit-high cards instead of 128, with rank gap 140
  instead of 128 and sibling gap 44 instead of 36. This opens the gaps modestly
  while reducing vertical pitch 164 → 156. Widths/routing margins stay unchanged.
- **D3 zoom** applies one transform to cards and SVG. The viewport clips overflow;
  panning is unconstrained and scale is 12–250%. Wheel/pinch anchoring and drag
  event handling come from the library. Framing/zoom buttons animate except under
  reduced-motion preferences. Resizing does not refit or reflow the graph.
- **Native headline rasterization** has no permanent `will-change: transform`
  hint on the world. Removing that hint visibly sharpened text (and SVG) in a
  same-pose 250% before/after Chromium check without changing font/world sizes or
  replacing native text. Browser/OS antialiasing and large-graph performance remain
  platform-dependent; this is not a universal text-quality/performance proof.
- **Native forms** retain text editing, selection, scrolling, resize, keyboard
  controls, drafts, and original node records for overwrite-conflict confirmation. Camera gestures are
  excluded from settings controls. Navigation alone sends no mutation commands.
- **Connection hover** temporarily emphasizes both SVG pieces of each immediate
  incoming/outgoing relationship. Colored Git/draft ink gains lightness and chroma
  in its own hue using relative OKLCH; mixing it with white/theme foreground washed
  out the requested colors. Neutral normal links retain theme contrast mixing.
  Pair ordering and full opacity improve visibility without enlarging strokes/heads
  or changing routes, dashes, or layout. Hovered node borders likewise strengthen
  their semantic hue; only the neutral gray manifesto in distance/type modes gets
  a white hover border. The new revision mode colors the manifesto by comparison
  kind, retaining that hue on hover. Delegated pointer transitions include expanded form controls; hit tests
  reconcile redraw/camera changes, and exit/blur/touch clears emphasis. No host
  messages, canonical data, or persisted hover preferences are involved.
- **Node colors** share a nine-step softly colored violet-to-red table, with
  slightly stronger chroma (.12 instead of .11) at unchanged lightness (.73).
  Distance one starts violet, nine ends red, then repeats. Type mode uses teal/violet;
  gray manifesto zero remains outside both distance/type palettes. Git/Revision
  Status instead uses rainbow green A, blue M/R, red D and amber source impact,
  including on the manifesto. Unchanged/no-comparison/draft fills are neutral;
  source-only, rename and withdrawal labels preserve their distinct meanings.
  Existing title/letter theme colors and connection inks stay independent.
- **Temporary label preview** cycles card-chrome right-clicks through red, blue,
  green, purple, turquoise, yellow and none. A six-pixel equal inset outline keeps
  card/port geometry unchanged and preserves native field/control context menus.
  Labels live only in renderer memory, not host state or canonical data, and reset
  on view reload. Persistence will likely be explored later; it is not implemented.
- **Webview state** holds overview/per-node camera preferences and drafts. No
  layout positions, magnification, colors, or derived scores enter `_specspec`.

## Why change the initial heuristic?

On the preceding 42-node snapshot, network-simplex placed the six immediate
manifesto children in ranks **4, 5, 3, 5, 1, 5**. Shared downstream nodes shortened
their connections by pulling early intentions rightward. Reversed longest-path
ranking places those six in rank **1** without changing a canonical edge. On that
same snapshot, mean visual rank fell from 5.95 to 4.48. This is evidence of fixing
the observed bias, not a universal density/optimality score or a stored taxonomy.
Earliest ranks alone still left the root's six direct neighbors vertically spread
by sink alignment. On the same later 45-node snapshot, a rank-preserving placement
backbone reduced their world-space span from 3792 to 1030, and total layout height
from 3952 to 2092. The final graph also includes this separately reasoned packing
choice. Neither comparison deletes a relationship or constitutes a universal
layout-quality guarantee.

## Build, licenses, and packaging

`npm --prefix graph-ui-common ci`, `npm --prefix vscode ci`, then `npm --prefix vscode run compile` builds
`vscode/media/vendor/graph-vendor.js` from the shared `graph-ui-common/src/graph-vendor.js` and generates
`THIRD_PARTY_NOTICES.txt` containing licenses for every bundled dependency.
Build artifacts are ignored in Git but included in extension packaging. Node
modules and build sources are excluded from the VSIX. The lockfile pins versions.
There are no CDN/runtime network requests, `eval`, or executable project Markdown.

## Verification and boundaries

Node tests cover left-to-right/earliest-root constraints, shallow branches feeding
shared deep sinks, vertical origin concentration with full relationship membership,
deterministic ordering, skipped-rank routing, historical rank
isolation, strong bends, head-base tangent joins, screen-strength floors, dash
visibility, pointer-anchored zoom, zoom bounds, viewport invariance, independent
cameras, native-control exclusions, keyboard navigation, caret preservation, and
the earlier editor/bridge/trust regressions.

`npm --prefix vscode run test:host` opens installed VS Code in a disposable profile.
Chromium checks the real graph, focuses nodes, pans/zooms, narrows the canvas,
resizes a textarea, samples centerlines and stroke-normal boundaries for content
intersections, verifies actual earliest ranks and vertical origin concentration,
checks tangent/head joins and screen
strength at 12% zoom, four color modes and revision-local bounds, label-free
shorter-card fit, same-pose native headline rendering at 250%, confirms circle-free endpoints, visits a real multiple-depth
parent neighborhood, restores the overview camera, and switches semantic colors. Optional
`SPECSPEC_SCREENSHOT_DIR` captures screenshots of overview and focused views;
`SPECSPEC_SCREENSHOT_FILTER` optionally restricts capture to names containing that
substring (for example `label-preview`) without skipping any assertions. The
agent inspected these on Windows; this does not replace full human editing/review
or revision-picker verification. Only this isolated automated test disables trust.

The current layout is synchronous and renders all nodes. Large-graph virtualization,
manual node dragging/reparenting, minimaps, configurable Blender keymaps, and
language-resolved source navigation remain out of scope. Crossing reduction is a
layout heuristic, not a guarantee of an optimal diagram for every possible graph.

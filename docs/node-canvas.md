# Node-canvas implementation rationale

This is noncanonical design/evidence context. The [graph tour](own-spec.md#neighborhood-ui-revision)
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

## Canvas controls

The full canvas holds a compact rounded navigation control at its bottom center.
Use − / + for zoom and the percentage for actual size. The framing icons are
**Frame graph**, contextual **Frame node**, and **Frame rectangle**. The color legend
shows swatches or a continuous ramp with short endpoint labels; the selected mode
names its meaning. These controls share both hosts.

Click Frame rectangle to arm one drag, or hold **Ctrl** over the canvas on
Windows/Linux (**Command** on macOS). The cursor becomes a crosshair. Releasing
the modifier before pressing restores the ordinary cursor. Press the primary mouse
button, drag in any direction, then release to frame the rectangle. A visible band
tracks the drag; releasing the modifier during that drag keeps the tool active.
Mouse release completes it even outside the canvas. A held modifier rearms after
release and a fresh press. Click the icon again or press Escape to cancel; blur,
pointer cancellation and capture loss also cancel. Tiny gestures under four pixels
on either axis retain the camera.

Rectangle framing uses the starting camera's inverse transform, 40 screen pixels
of margin and the existing 250% maximum. Graph/node framing retains its 100% cap.
Wheel/pan/camera keys pause during an active rectangle drag. Native controls and
links keep their interactions. Shift-click highlight cycling and Ctrl/Command+Shift
clearing keep precedence. Physical macOS interaction remains unqualified; the
Command mapping has synthetic-event coverage.

## Overview paint

From 40% down to 16% zoom, node backgrounds progressively become their painted
border color. Ordinary arrows darken on a separate 70%-to-16% interval. Let
`q = 1 - clamp((k-.16)/(.40-.16), 0, 1)`. First form the exact actual-size 15%
accent resting tint or 24% accent hover tint; then mix that base toward the currently
painted border by `q`. High-contrast cards start from the theme canvas background.
At 16% and below, fills match borders, including emphasized colored borders and
the hovered neutral manifesto's white border. At this altitude shapes and colors
carry the overview; text keeps its ordinary styling. Zoom changes only inherited
paint variables and edge compensation.

## Separation of responsibilities

- **Python** validates schemas, links, physical deletion and writes.
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
  Ordinary attachments span intrinsic card heights instead of a narrow title band;
  manifesto ports span its middle arc and attach at the actual circle chord. A short
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
  backbone. Legends show concise hop swatches; the mode selector names the metric.
  Downstream, Git, and source-impact cues remain independent.
- **Influence fills** count unique descendants at every depth. Absolute influence
  uses `count / highestNonManifestoCount`; Relative influence uses
  `(count - cohortMin) / (cohortMax - cohortMin)`, grouping by maximum manifesto
  distance. Log Absolute Influence uses `log1p(count) / log1p(maximum)`, while
  Log Relative Influence uses `(log1p(count) - log1p(cohortMin)) /
  (log1p(cohortMax) - log1p(cohortMin))`. Transform raw counts before normalization,
  with the +1 defining zero. All four choices remain available. Zero denominators
  use green, including equal positive counts and singletons. The manifesto remains neutral gray. Full target/base revisions supply
  the ranges independently of focus and comparison unions. Raw ranges/counts are
  lazy per metrics instance and shared by linear/log modes. Continuous sRGB interpolation through green `#4df884`,
  yellow `#e8d62c` and red `#ba2208` gives a warm Turbo-like ramp with no blue;
  a matching continuous gradient legend labels its endpoints. Native drafts,
  geometry/camera, Git cues and spotlight rings retain their independent roles.
- **Compact spacing** uses ordinary 112-unit-high cards instead of 128, with rank gap 140
  instead of 128 and sibling gap 44 instead of 36. This opens the gaps modestly
  while reducing vertical pitch 164 → 156. Widths/routing margins stay unchanged.
- **Type shapes** use completely square 0px implementation corners,
  24px requirement corners (slightly rounder than the former 20px Implementation),
  and a true square/50%-radius manifesto, including expanded editing. Compact
  manifesto diameter is 264; expanded diameter is the 822px-wide native form's
  rectangle diagonal plus 48px, rounded up. Center the same form DOM without
  clipping controls or reducing the 80-column content budget. The larger outer
  footprint is a deliberate cost of a genuinely circular editor. Arc/corner-aware
  ports retain 3-unit clearance; circle ports span the middle 40% vertically so
  thick minimum-zoom strokes clear the arc. Flat departure/settling segments clear
  conservative bounding boxes before curves turn. Git markers move inside the
  circle; palettes, tints, hover and spotlight inset rings retain their independent roles. The offline
  playground's gray manifesto sample is likewise circular, without changing exports.
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
  their semantic hue; only the neutral gray manifesto in distance/type/influence modes gets
  a white hover border. The new revision mode colors the manifesto by comparison
  kind, retaining that hue on hover. Delegated pointer transitions include expanded form controls; hit tests
  reconcile redraw/camera changes, and exit/blur/touch clears emphasis. No host
  messages, canonical data, or persisted hover preferences are involved.
- **Distance/type/revision colors** share the user's exact seven-color playground table, with
  confirmed parameters L=.69, C=.12, hue 320 → 20. Distance one starts at the first
  swatch, seven ends at the last, then repeats. Type mode uses yellow-green/purple; Added uses the teal-green closer to its text cue;
  gray manifesto zero remains outside both distance/type palettes. Git/Revision
  Status instead uses rainbow green A, blue M/R, red D and amber source impact,
  including on the manifesto. Unchanged/no-comparison/draft fills are neutral;
  source-only, rename and deletion labels preserve their distinct meanings.
  Existing title/letter theme colors and connection inks stay independent.
- **Spotlights** persist message/ID/comparison metadata in Git-excluded project-local
  storage shared by the CLI and both hosts. Git owns committed node text. A round red toolbar badge
  counts new batches since this view last opened its list; existing initial entries
  count zero. Opening the list clears the count, and reload starts a new in-memory
  baseline. Arrivals preserve editing, focus and camera. A newest-first dropdown
  anchored to Spotlights shows one text entry per spotlight. Selection activates
  its comparison, closes the dropdown and frames available IDs (including deleted
  base nodes) with camera-scaled white inset rings, retaining focused drafts.
  Edit --spotlight-color in shared graph.css to try another ink. Shift-click toggles
  manual/spotlight membership; Ctrl/Command+Shift-click clears a node. Workspace
  drift warns visibly while highlighting the best available nodes. The dropdown
  saves highlights with a message/current comparison without saving documents/forms.
  IDs and active spotlight preferences are per view; immutable metadata survives
  sessions until explicit flush. See [spotlight design and storage](spotlights.md).
- **Ordinary arrows** use darker shared neutral ink, mixed with black at 70% at
  70% scale and above, decreasing linearly to 35% at 16% and below. The existing
  curve/head pair and minimum pixel dimensions remain intact. Diff/draft colors and
  incident-hover emphasis keep independent paint so the overview mesh stays quiet
  beside spotlight batches.
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

`test/camera.test.cjs` covers inverse bounds, each drag direction, modifier hover
and release, held-modifier one-shot completion, tiny/cancelled drags, pointer identity,
window release, cursor cleanup, disposal, native controls and synthetic Mac gestures.
Renderer tests check floating/contextual controls, concise legends, literal project
text and preservation of editing/caret/world state during camera changes.
`test-host/canvas.cjs` runs early in both installed suites: dark/light/contrast fills
at three scales, the white hover endpoint, floating controls, modifier latching,
actual Chromium pointer capture/outside release and native selection preservation.
Installed phase outcomes are recorded separately in the smoke investigation.


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
strength at 12% zoom, eight color choices and revision-local bounds, label-free
shorter-card fit, same-pose native headline rendering at 250%, confirms circle-free endpoints, visits a real multiple-depth
parent neighborhood, restores the overview camera, and switches semantic colors. Optional
`SPECSPEC_SCREENSHOT_DIR` captures screenshots of overview and focused views;
`SPECSPEC_SCREENSHOT_FILTER` optionally restricts capture to names containing that
substring (for example `spotlights`) without skipping any assertions. The
agent inspected these on Windows; this does not replace full human editing/review
or revision-picker verification. Only this isolated automated test disables trust.

The current layout is synchronous and renders all nodes. Large-graph virtualization,
manual node dragging/reparenting, minimaps, configurable Blender keymaps, and
language-resolved source navigation remain out of scope. Crossing reduction is a
layout heuristic, not a guarantee of an optimal diagram for every possible graph.

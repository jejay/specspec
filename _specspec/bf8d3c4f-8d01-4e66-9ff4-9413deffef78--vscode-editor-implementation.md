---
id: bf8d3c4f-8d01-4e66-9ff4-9413deffef78
type: implementation
parents:
- 02a4e457-d709-40af-979c-1216064b1f82
- 10ef1cdc-62a6-4212-8387-704d3cbbeeb4
- 1ba7e336-cdc2-46a9-8118-4b8f9e92057b
- 1f2e42c3-331f-4c1c-adc7-897f9bf2e004
- 2b6a0e4e-f07f-4932-b58b-40348d4c3ac1
- 2b8a4bbc-d15a-4347-90b4-691abdeefaef
- 4254f33d-ce29-4e33-830e-28a8edd2a51c
- 51c3e963-674e-4d5d-bd7a-b8d63649e1c8
- adb5a4c8-f9c5-4bcc-b38b-8584d469cf25
- c2ed5444-b7b2-4c2a-901c-ab1ba64e5e54
- ca580dc7-c7fa-48bc-91b1-59243144a0bf
- d70cdad5-5e03-4200-ac75-74cf6514e56c
- f65750b7-0e8c-4014-b209-e2b480ab26d2
- fbaee7c1-4c20-47ab-afd2-ae0503d428b5
sources:
- path: docs/node-canvas.md
- path: tests/test_migration.py
  symbol: versioned backend compatibility
- path: vscode/.vscodeignore
- path: vscode/LICENSE
- path: vscode/media/graph-camera.js
  symbol: createCamera
- path: vscode/media/graph-model.js
  symbol: edgeAppearance
- path: vscode/media/graph-model.js
  symbol: layoutBackbone
- path: vscode/media/graph-model.js
  symbol: layoutGraph
- path: vscode/media/graph-model.js
  symbol: metrics
- path: vscode/media/graph.css
- path: vscode/media/graph.css
  symbol: incident-highlight contrast and Git ink
- path: vscode/media/graph.js
- path: vscode/media/graph.js
  symbol: legacyWorkspace and withdrawal presentation
- path: vscode/media/graph.js
  symbol: trackHover, syncHover, updateEdgeHighlights
- path: vscode/package-lock.json
- path: vscode/package.json
- path: vscode/scripts/build-webview.cjs
- path: vscode/src/bridge.ts
  symbol: invoke
- path: vscode/src/extension.ts
  symbol: GraphPanel
- path: vscode/src/extension.ts
  symbol: GraphPanel.handleMessage migration and withdrawal guards
- path: vscode/src/graph-vendor.js
- path: vscode/src/project.ts
  symbol: findProjectRoot
- path: vscode/src/view.ts
  symbol: graphHtml
- path: vscode/test-host/run.cjs
- path: vscode/test-host/smoke.cjs
- path: vscode/test-host/ui.cjs
- path: vscode/test-host/ui.cjs
  symbol: checkHover computed paint and unchanged geometry
- path: vscode/test/bridge.test.cjs
- path: vscode/test/extension.test.cjs
- path: vscode/test/graph-model.test.cjs
- path: vscode/test/graph.test.cjs
- path: vscode/test/graph.test.cjs
  symbol: hover membership, native forms, lifecycle and revision regressions
- path: vscode/test/project.test.cjs
- path: vscode/media/graph-model.js
  symbol: metrics minDistances/maxDistances; CARD_HEIGHT, RANK_GAP, NODE_GAP
- path: vscode/media/graph.js
  symbol: distanceFor, drawLegend, compactCard, loadForm
- path: vscode/media/graph.css
  symbol: shorter cards, empty badge rows, unhinted world text
- path: vscode/src/view.ts
  symbol: Min./Max. Distance to Manifesto selector labels
- path: vscode/test/graph-model.test.cjs
  symbol: path bounds, defensive cycles/deep graphs, spacing
- path: vscode/test/graph.test.cjs
  symbol: distance modes/revisions/preferences, labels, native drafts/text
- path: vscode/test-host/ui.cjs
  symbol: checkHeadlineRendering and independent min/max path checks
managed_hash: 45b075717af3f7a0acc35ff5da8e0d6a44c91e4dd743961d0979dba3111cad1a
---
# Display, navigate, edit, and compare graphs through the CLI

The extension host launches the Python JSON CLI with bounded, shell-free processes.
The nonce-protected local webview renders an overview or focused neighborhood;
the same native form DOM moves into the expanded selected node. Managed writes,
actual parent links/candidate choices, explicit withdrawal/restoration, workspace
trust, read-only history, stale-fingerprint drafts, Git overlays, startup logs,
and token-matched complete-render checks remain separate from presentation.

Dagre receives stably ordered node IDs/relations and intrinsic card dimensions.
Reversed input and its RL longest-path ranker produce visible LR earliest-source
ranks: one plus the maximum parent rank, not a sink-biased network-simplex result.
Short branches and the manifesto's immediate intentions remain near the origin.
The overview/current focus uses target relationships; a removed selected node uses
base context. Extra references into primary nodes remain overlays, not constraints
that shift live ranks. Historical branches with nonprimary children stay visible. Compute ranks from
all parents, then use a deterministic deepest-parent placement backbone to keep
early branches vertically compact rather than aligned to distant common sinks.
Every canonical/overlaid edge is still routed; this forest is not a preference or
a change to dependency metadata.
This changes presentation, not canonical dependencies; full-snapshot path metrics remain separate.

No viewport size enters arrangement. Compact and expanded widths are fixed world
sizes; expanded height is measured without camera scale. Inputs are cached and
resizing preserves the focused card's screen anchor and existing form/caret.
Narrowing the viewport clips the same world rather than wrapping its nodes.

D3 shape connects right and left boundaries directly, without connector circles.
Attachments span intrinsic card height, including expanded forms, instead of a
small title band. Skipped-rank lanes remain flat across complete card-width bands
before curving through gaps. Non-backbone forward references without engine guides choose the nearest clear
gaps across skipped columns, with outer corridors as fallback; reverse links use a loop with the same tangent-aligned arrival.

A short horizontal departure prevents steep thickened curves from brushing the
source card. A 64-world-unit settling approach accommodates the largest supported
low-zoom arrowhead. The curve joins it tangentially. The stroked line stops at the
filled head's base, avoiding a line protruding through the tapered arrow tip.
Camera updates compensate stroke width to at least 1.6 CSS screen pixels and head
length to at least 6 pixels, while retaining normal world sizes at higher zoom.
Git dash lengths are compensated too. Those are implementation constants, not
user-prescribed canonical scores. Zoom updates the same edge DOM only, with no
relayout or form recreation. Git strokes/badges stay distinct from semantic fills.

D3 zoom supplies one camera transform for native DOM and SVG, without a permanent compositor-promotion hint. Middle-drag/background drag
pans without world-bound clamping; wheel/pinch zoom anchors at the pointer, bounded
at 12-250 percent. Buttons and keyboard actions restore actual size or frame the
view, with reduced-motion-aware transitions. Separate overview/focus cameras and
drafts persist in webview state. Native text/control gestures are excluded;
navigation sends no mutation commands. The adaptive grid and navigation strip do
not cover save/review controls. No position, camera, color, or metric is canonical.

Minimum/maximum manifesto path colors replace repeated on-node hop labels. Child badges count all distinct
reachable downstream IDs at every depth, excluding that child; shared paths are
deduplicated per child and overlapping totals are not additive. Removed nodes use
base metrics and surviving nodes use target metrics, never the revision union.

The local build bundles pinned Dagre/D3 modules and all transitive license notices;
it requires no CDN, remote renderer, executable project Markdown, or Blender port.
A local VSIX build has been checked to include the offline assets and both project
and dependency licenses, excluding node_modules and build/test sources.
The library rationale documents revisable choices, not a confidence score or individual approval stage.

Verification includes TypeScript compilation, 85 bridge/activation/DOM/model tests,
68 Python tests, Ruff, and warnings-as-errors graph validation. Regression fixtures
cover shallow branches sharing deep sinks, earliest ranks versus shortest hops,
historical rank isolation, extreme bends, scaled width/head floors, dash patterns,
full-height attachments, circle-free joins, and existing draft/trust/history/text
safety. The supported camera limit is checked against settling/head clearance.

Installed VS Code/Chromium on Windows has rendered the current 51-node graph and
verified each live node's earliest allowed rank and compact vertical origin
neighborhood, including all seven immediate manifesto children in rank one. It has checked actual screen strength at 12 percent
zoom, head-base/tangent joins, no circles, sampled painted-stroke boundaries for
card/content intersections, inspected a real multiple-depth parent neighborhood,
resized an intrinsic textarea, and retained navigation/cameras/native gestures.
Overview, minimum-zoom, focused, resized, and multiple-parent screenshots were
captured and visually inspected. A local offline VSIX build verifies assets and
project/dependency licenses without node_modules/build/test sources.

Full manual mutation/review and revision-picker verification remain outstanding.
Synchronous layout and full DOM rendering are not large-graph virtualization or a
guarantee of an optimal/crossing-free diagram for every possible specification.
Implementation is an attempt under the user's review/risk budget; its choices remain revisable.


## Approval-free review workflow

The TypeScript bridge requires JSON API two and represents withdrawal as a boolean.
There is no acceptance message/action, status dataset, or approval-colored fill.
Save node writes without a sign-off transition. Retire/Restore are confirmed
withdrawal actions, and legacy workspaces offer confirmed whole-graph migration
through the guarded CLI. History cannot migrate, untrusted workspaces cannot run
tools, and dirty/restored drafts never acquire a new fingerprint silently.

Distance-first fills and existing-node-type fills explain their meaning without
encoding confidence. Obsolete saved status-mode preferences fall back to distance
while preserving forms, drafts, cameras, caret, and selection. Withdrawn compact
cards show a separate label, independent of added/changed/source-change badges.

DOM/host tests cover absent approval controls, guarded retire/restore, removed
accept messages, legacy read-only forms, explicit/cancelled/stale migration,
historical/trust restrictions, dirty-draft preservation, and API-one rejection.
The real Windows VS Code/Chromium check passed on 49 nodes with approval-free
controls, withdrawal labels, both palettes, and the existing geometry/navigation
regressions. Removed links can share/reverse columns as historical overlays;
only target relationships impose LR ranks. All curves, including those old links,
were checked for tangent joins and sampled painted-stroke/content clearance.
Screenshots of overview/focus/root and other navigation cases were inspected.

## Transient incident-connection hover

Delegated pointerover/move/out events on the viewport resolve the containing card
by full node ID. Entering controls inside the same expanded card does not flicker
or disturb native editing. A transient hovered ID and pointer position never enter
canonical data, persisted drafts/cameras, selection, or host/CLI messages. Exit,
window blur, pointer cancellation, and touch clear emphasis. Redraw and camera
changes use elementFromPoint to reconcile the actual card under a stationary
pointer rather than carrying stale hover into another view.

updateEdgeHighlights toggles incident-highlight on each existing curve/head pair
whose parent or child matches the hovered ID. It raises those SVG pairs above
other connections and restores original ordering on exit. CSS mixes each existing
Git ink with theme foreground and uses full opacity, preserving hue/classes and
camera-compensated dashes. It changes no path, stroke/head dimension, glow, hit
area, layout, camera, form DOM, caret, or fingerprint. SVG remains non-interactive.
Overview, focused expanded cards, read-only history, removed links, and unsaved
draft links share this display-only behavior.

Seven new DOM regressions verify exact direct membership and paired heads,
unchanged geometry/DOM identity/preferences/messages, native drafts/caret,
transitions/exit/blur/cancel/touch, historical added/removed styling, isolated and
linked drafts, refresh/hit reconciliation, and disappearing cards/navigation.
The installed Windows VS Code/Chromium check passed with 49 nodes, checking actual
computed curve/head paint and restored SVG order in overview, over a focused
textarea, and at minimum zoom. Hover leaves width/dash/path/head geometry and
world/camera unchanged; existing painted-stroke clearance checks still passed.
Hover overview/focus/minimum-zoom screenshots were captured and inspected.

## Minimum/maximum paths, modest spacing, and sharp high-zoom text

metrics derives minDistances by iterative breadth-first traversal and maxDistances
by topological dynamic programming over every snapshot relationship. Deduplicated
children/indegrees handle repeated/shared paths; maximum is only published once
all parents are processed. Defensive cycles and blocked descendants have unknown
maximums, not finite invented depths. Both root distances are zero; unreachable
nodes have neutral fills. Deep 6,000-node fixtures avoid recursion. Surviving nodes
use target metrics and removed nodes use base, never the cyclic display union or
visible placement forest. Maximum equals longest root path, not confidence.

The selector labels are Min. Distance to Manifesto, Max. Distance to Manifesto,
and Node type. Existing distance preferences/defaults remain minimum; maximum
persists separately, and obsolete status preferences still fall back safely.
Legends explain shortest/longest directed paths. Compact and expanded nodes no
longer repeat hop-distance text. Downstream, Git, and withdrawn labels remain.
Switching fills retains positions/camera, actual parent links, native form identity,
caret/selection, dirty draft, and original fingerprint; no mutation is emitted.

Compact cards are 264 by 112 world units instead of 264 by 128. Dagre rank gap
increases 128 to 140 and sibling gap 36 to 44: modestly more breathing room while
vertical pitch decreases 164 to 156. Empty badge rows are hidden. Expanded width,
intrinsic height measurement, all-parent ranks/backbone, routing margins, hover,
screen-strength floors, and viewport independence remain unchanged. Real browser
checks confirmed two-line headings/remaining badges fit without card overflow.

Removing permanent will-change: transform from the world allows native text and
SVG to repaint at the current scale instead of magnifying a cached low-scale
surface. No font-size override, bitmap/canvas label, counter-scale, new layer, or
form recreation is introduced. The installed VS Code A/B probe temporarily restored
the old hint before zooming to 250 percent, then removed it at the exact same camera
pose. Inspected before/after screenshots show markedly sharper headlines, metadata,
and curves. Computed font sizes, intrinsic headline/world geometry, text content,
and DOM identity stayed unchanged. Screen-scale checks account for host CSS zoom;
synthetic pan restoration permits Chromium's integer client-coordinate rounding.
This is platform-specific visual evidence, not identical antialiasing/performance
for every browser, OS, or device.

Eight additional model/DOM regressions cover bounds, defensive cycles/order/edges,
spacing/pitch, exact mode labels, absence of node hop text, distinct fills/legends,
full-snapshot revision metrics, preference restoration, stale dirty drafts/caret,
and high-zoom native text geometry. All 85 editor and 68 Python tests passed, along
with TypeScript compilation, JS syntax, Ruff, and warnings-as-errors graph checks.
Installed Windows VS Code/Chromium passed on 51 nodes, independently checked path
bounds for each node, and retained earliest ranks, full relationship membership,
hover, low-zoom arrows, native gestures/cameras, and resized painted-stroke clearance.
Minimum/maximum overview, focused, and same-pose 250-percent text images were captured
and inspected. Full manual mutation/revision workflows and large-graph optimization
remain separate verification boundaries.

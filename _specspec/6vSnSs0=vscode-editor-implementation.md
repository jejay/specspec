---
id: 6vSnSs0=
type: implementation
parents:
- NsFLK9o=
- fdB9ZLM=
- 2XVN2Jo=
- -0ljwrM=
- qnGsij4=
- V0xi_J8=
- bOXyw00=
- aiuyGEs=
- SRsw2W0=
- ALlkmT0=
- eLTZ3sg=
- 3jX0Rgk=
- apEb_pM=
- mAZgRy8=
- GQdmCrA=
- FHfnj08=
- tgHQyx4=
sources:
- path: branding/activity-icon.svg
  symbol: Activity Bar mask
- path: docs/node-canvas.md
- path: graph-ui-common/host/session.cjs
  symbol: shared guarded session
- path: graph-ui-common/media/graph-camera.js
  symbol: createCamera
- path: graph-ui-common/media/graph-model.js
  symbol: edgeAppearance
- path: graph-ui-common/media/graph-model.js
  symbol: layoutBackbone
- path: graph-ui-common/media/graph-model.js
  symbol: layoutGraph
- path: graph-ui-common/media/graph-model.js
  symbol: metrics minDistances/maxDistances; CARD_HEIGHT, RANK_GAP, NODE_GAP
- path: graph-ui-common/media/graph-model.js
  symbol: metrics
- path: graph-ui-common/media/graph.css
  symbol: git title/corner tokens and narrow host chrome
- path: graph-ui-common/media/graph.css
  symbol: incident-highlight/hover-darkened paint, neutral manifesto and Git ink
- path: graph-ui-common/media/graph.css
  symbol: shorter cards, empty badge rows, unhinted world text
- path: graph-ui-common/media/graph.css
- path: graph-ui-common/media/graph.js
  symbol: distanceFor, drawLegend, compactCard, loadForm
- path: graph-ui-common/media/graph.js
  symbol: invalid-workspace diagnostics and HEAD deletion presentation
- path: graph-ui-common/media/graph.js
  symbol: trackHover, syncHover, updateHoverAppearance
- path: graph-ui-common/media/graph.js
- path: graph-ui-common/src/graph-vendor.js
- path: graph-ui-common/test-host/platform.cjs
  symbol: actual Git title/corner/theme checks
- path: graph-ui-common/test-host/ui.cjs
  symbol: shared real-host geometry/hover/metrics
- path: graph-ui-common/test/graph-model.test.cjs
  symbol: path bounds, defensive cycles/deep graphs, spacing
- path: graph-ui-common/test/graph-model.test.cjs
- path: graph-ui-common/test/graph.test.cjs
  symbol: distance modes/revisions/preferences, labels, native drafts/text
- path: graph-ui-common/test/graph.test.cjs
  symbol: hover membership, native forms, lifecycle and revision regressions
- path: graph-ui-common/test/graph.test.cjs
- path: graph-ui-common/view.cjs
  symbol: single HTML shell
- path: tests/test_ids.py
  symbol: canonical IDs, current-only validation and collision retry
- path: vscode/.vscodeignore
- path: vscode/LICENSE
- path: vscode/package-lock.json
- path: vscode/package.json
- path: vscode/scripts/build-webview.cjs
- path: vscode/src/bridge.ts
  symbol: invoke
- path: vscode/src/extension.ts
  symbol: GraphEditors, GraphProject, GraphView
- path: vscode/src/extension.ts
  symbol: GraphEditors, GraphProject, GraphView
- path: vscode/src/host.js
  symbol: project-scoped messaging/state adapter
- path: vscode/src/project.ts
  symbol: findProjectRoot
- path: vscode/src/view.ts
  symbol: Min./Max. Distance to Manifesto selector labels
- path: vscode/src/view.ts
  symbol: graphHtml
- path: vscode/test-host/run.cjs
- path: vscode/test-host/smoke.cjs
- path: vscode/test-host/ui.cjs
  symbol: checkHeadlineRendering and independent min/max path checks
- path: vscode/test-host/ui.cjs
  symbol: checkHover computed paint and unchanged geometry
- path: vscode/test-host/ui.cjs
- path: vscode/test/bridge.test.cjs
- path: vscode/test/extension.test.cjs
- path: vscode/test/host.test.cjs
  symbol: port state/draft isolation
- path: vscode/test/project.test.cjs
---
## Current deletion-only correction

xu6W0c4=/5d5oDCM= supersede the earlier retired/withdrawal workflow below.
Current schema/API 5 removes the flag and all retire/restore/filter/metadata/badge
paths. Managed delete physically unlinks an explicit batch after DAG checks,
with journal new=null and original-byte/recovery safeguards. Default HEAD-relative
UI ghosts are derived base records, read-only/copyable through staging and gone
after commit; Git HEAD/ref watching refreshes both hosts. Native Delete requires
clean project documents; deleted buffers never resurrect files in overlay reads.
All earlier workflow/schema/test counts below are historical evidence. Gantt's
entire current corpus is rebuilt with 22 physical deletions/reasons in prior Git
commits and a 22-node HEAD, no flagged retained nodes. Earlier root explanations
are in Git, not retained retired files. Source regions/colors/shapes/camera/native
Save remain in scope; the separate current implementation record links actual tests.

## Current compact-ID and history correction

The implementation/verification below records earlier revisions. Its legacy-reader,
schema-migration, original API-2 receipt and root-history compatibility descriptions
are superseded by qowy5AI= and YaXJpGE=. Current production code supports only the
canonical Base64url node scheme, with no old-schema reader or migration command.
The default node-editor association is **/_specspec/???????=*.md. Gantt's maintained
history is rewritten and bundled; tests do not require old root graph revisions.
Earlier run counts are historical evidence, not claims about this revision. The
separate current implementation record documents the new checks and limitations.

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

Installed VS Code/Chromium on Windows has rendered the then-current 51-node graph and
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


## Shared UI extraction checkpoint

The renderer/model/camera/CSS and DOM/model tests now have their single source in graph-ui-common. The editor wrapper delegates the template, bounded CLI/discovery and guarded GraphSession, while keeping VS Code authorization, dialogs, watching and messages. Historical test counts above remain original evidence. All 68 common and 23 editor-adapter tests pass at this checkpoint; six new shared-session tests strengthen modern fingerprint/complete-render and authorization/disposal guards. Twelve bundled license notices remain. Activity Bar, branding/Git cues and Electron are planned next, not claimed already implemented here.


## Activity Bar host and Git/brand correction

The graph now lives in one retained Activity Bar WebviewView, not an editor tab.
GraphViewProvider serializes project opens, finishes pending old-root operations,
resolves nested graphs, and focuses the existing view. Open project/Select Project
and Explorer-folder Open Graph work without reopening the workspace. Renderer
state is project-scoped; reload/switch never share dirty drafts between roots.
Settings remain inline. The narrow host chrome adapts but cards/layout do not reflow.
VS Code assigns extension containers after built-ins; inspection corrected the
unsupported order-4 proposal. Drag the dachshund below Run/Debug if preferred;
no private API or user-layout overwrite is used. The minimal mask/full package
icon are built from branding assets, not hand-maintained platform copies.

Shared CSS colors compact/expanded titles and bottom-right A/M/D/R from theme
tokens. M deliberately uses modified-gutter blue instead of amber resource text.
Source-only hints keep their own badge and do not invent M; withdrawal isn't D.
Semantic fills, edge colors/dashes, geometry, fingerprints and native forms remain.
All 72 common and 27 VS Code adapter tests pass. New tests cover exact corner kinds,
source/withdrawal distinctions, native dirty/caret/camera retention, token defaults,
scoped port state, direct icon activation and nested switching in the same view.
Real installed Windows VS Code on a disposable canonical/Git fixture passed the
same canvas/paint suite as Electron, including A/M/D, live theme changes, clipped
sidebar hover and complete geometry/path metrics. Sidebar and miniature icon
screenshots were inspected. Prior 51-node/full-editor-tab evidence remains historical,
not a claim that today's surface or counts were tested then. Native project/revision
pickers and complete manual workflows remain distinct from dispatched tests.


## Hash-free Markdown synchronization revision

The later manual-edit intention and separate hash-free/watcher conclusion supersede
all earlier API-2/fingerprint/stale-hash claims in this record. Current code uses
API/format 3, no managed_hash or fingerprint gate, and permits valid manual edits.
Original detailed test counts and packaged-host evidence above remain historical,
not claims of re-running every old package or platform against this revision.

GraphSession coalesces watcher events, retries failed reads twice, compares records
directly and validates current files before UI writes. Render sequence/full-membership
checks remain without fingerprint acknowledgements. Dirty drafts retain original
node records/caret/camera; unrelated changes permit saving, same-node overwrites ask
confirmation, and deletion/invalid files preserve copyable drafts. Invalid reloads
mark the last valid graph out of date and disable mutations until a valid reload.
VS Code watches directory/files; Electron's shared GraphWatcher also watches the
parent and reattaches after canonical-directory recreation. Optional configurable
polling defaults to zero/off and is disposed with sessions. No silent fallback,
universal event-delivery guarantee or adversarial race-free writes are claimed.

The independent Gantt working graph was migrated without changing body/relationship
semantics. Its original CLI receipts/Git commits are retained verbatim. The history
verifier now reconstructs records and compares actual contents directly; archived
hash strings are opaque receipt labels, not a current hash algorithm or edit gate.
See the separate current implementation record for source links and final checks.


## Installed VS Code recheck before the authorized commit

The user requested another real VS Code run after the earlier executable-update
block. All 29 editor adapter tests and the installed Windows host smoke now pass,
including complete 69-node target/70-node display rendering, watcher-only manual
Markdown synchronization, deliberate invalid-file diagnostics/recovery without
rewriting those files, and preserved drafts/caret/camera/native controls. Both real
working graphs are valid with warnings as errors; deliberately malformed fixtures
are disposable and restored. No Linux/macOS or remote-CI run is inferred. See the
hash-free-markdown-sync implementation record for the current complete evidence.

## Native node-file editor correction

The current VS Code adapter replaces the preceding sidebar host with GraphEditors (CustomTextEditorProvider), reference-counted GraphProject document coordination and independent GraphView panels. Canonical node files open by default in the main editor, with raw text access; neighbors open their file editors and commit comparisons open independent panels. Native document saves/undo/dirty/recovery differ deliberately from Python-managed project/Electron writes. The old WebviewView conclusion is withdrawn and this live implementation is reconnected to the new native-document choice. A separate current implementation record links the non-writing planner, shared document ports, form recovery and verification boundaries. The earlier sidebar/API evidence remains history, not current hosting behavior.

## Neutral root and outside-hover context revision

6MUwTIw= extends the shared presentation with a fixed light-gray manifesto and
transient darkening outside immediate displayed hover relationships. The helper
is now updateHoverAppearance (formerly updateEdgeHighlights), reapplying card
and paired-edge membership after redraw even with unchanged hovered identity.
The separate current implementation record links source/tests and full Windows
host checks; the earlier counts and contrast-only descriptions remain history.

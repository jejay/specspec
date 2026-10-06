---
id: bf8d3c4f-8d01-4e66-9ff4-9413deffef78
type: implementation
status: proposed
parents:
- 10ef1cdc-62a6-4212-8387-704d3cbbeeb4
- 1f2e42c3-331f-4c1c-adc7-897f9bf2e004
- 2b6a0e4e-f07f-4932-b58b-40348d4c3ac1
- 2b8a4bbc-d15a-4347-90b4-691abdeefaef
- 4254f33d-ce29-4e33-830e-28a8edd2a51c
- 51c3e963-674e-4d5d-bd7a-b8d63649e1c8
- adb5a4c8-f9c5-4bcc-b38b-8584d469cf25
- d70cdad5-5e03-4200-ac75-74cf6514e56c
- fbaee7c1-4c20-47ab-afd2-ae0503d428b5
- c2ed5444-b7b2-4c2a-901c-ab1ba64e5e54
sources:
- path: docs/node-canvas.md
- path: vscode/.vscodeignore
- path: vscode/LICENSE
- path: vscode/media/graph-camera.js
  symbol: createCamera
- path: vscode/media/graph-model.js
  symbol: edgeAppearance
- path: vscode/media/graph-model.js
  symbol: layoutGraph
- path: vscode/media/graph-model.js
  symbol: metrics
- path: vscode/media/graph.css
- path: vscode/media/graph.js
- path: vscode/package-lock.json
- path: vscode/package.json
- path: vscode/scripts/build-webview.cjs
- path: vscode/src/bridge.ts
  symbol: invoke
- path: vscode/src/extension.ts
  symbol: GraphPanel
- path: vscode/src/graph-vendor.js
- path: vscode/src/project.ts
  symbol: findProjectRoot
- path: vscode/src/view.ts
  symbol: graphHtml
- path: vscode/test-host/run.cjs
- path: vscode/test-host/smoke.cjs
- path: vscode/test-host/ui.cjs
- path: vscode/test/bridge.test.cjs
- path: vscode/test/extension.test.cjs
- path: vscode/test/graph-model.test.cjs
- path: vscode/test/graph.test.cjs
- path: vscode/test/project.test.cjs
- path: vscode/media/graph-model.js
  symbol: layoutBackbone
managed_hash: 7f37146e67af688f1c3ee4ca95b13944c79370c716cbd4784a01923ddfbd8ac7
---
# Display, navigate, edit, and compare graphs through the CLI

The extension host launches the Python JSON CLI with bounded, shell-free processes.
The nonce-protected local webview renders an overview or focused neighborhood;
the same native form DOM moves into the expanded selected node. Managed writes,
actual parent links/candidate choices, explicit acceptance/retirement, workspace
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
This changes presentation, not any canonical dependency or shortest-hop metric.

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

D3 zoom supplies one camera transform for DOM and SVG. Middle-drag/background drag
pans without world-bound clamping; wheel/pinch zoom anchors at the pointer, bounded
at 12-250 percent. Buttons and keyboard actions restore actual size or frame the
view, with reduced-motion-aware transitions. Separate overview/focus cameras and
drafts persist in webview state. Native text/control gestures are excluded;
navigation sends no mutation commands. The adaptive grid and navigation strip do
not cover save/review controls. No position, camera, color, or metric is canonical.

Parent badges still use shortest manifesto hops. Child badges count all distinct
reachable downstream IDs at every depth, excluding that child; shared paths are
deduplicated per child and overlapping totals are not additive. Removed nodes use
base metrics and surviving nodes use target metrics, never the revision union.

The local build bundles pinned Dagre/D3 modules and all transitive license notices;
it requires no CDN, remote renderer, executable project Markdown, or Blender port.
A local VSIX build has been checked to include the offline assets and both project
and dependency licenses, excluding node_modules and build/test sources.
The library research/rationale is documentation, not acceptance of the proposals.

Verification includes TypeScript compilation, 59 bridge/activation/DOM/model tests,
53 Python tests, Ruff, and warnings-as-errors graph validation. Regression fixtures
cover shallow branches sharing deep sinks, earliest ranks versus shortest hops,
historical rank isolation, extreme bends, scaled width/head floors, dash patterns,
full-height attachments, circle-free joins, and existing draft/trust/history/text
safety. The supported camera limit is checked against settling/head clearance.

Installed VS Code/Chromium on Windows has rendered the current 46-node graph and
verified each live node's earliest allowed rank and compact vertical origin
neighborhood, including all six immediate manifesto children in rank one. It has checked actual screen strength at 12 percent
zoom, head-base/tangent joins, no circles, sampled painted-stroke boundaries for
card/content intersections, inspected a real multiple-depth parent neighborhood,
resized an intrinsic textarea, and retained navigation/cameras/native gestures.
Overview, minimum-zoom, focused, resized, and multiple-parent screenshots were
captured and visually inspected. A local offline VSIX build verifies assets and
project/dependency licenses without node_modules/build/test sources.

Full manual mutation/review and revision-picker verification remain outstanding.
Synchronous layout and full DOM rendering are not large-graph virtualization or a
guarantee of an optimal/crossing-free diagram for every possible specification.
Implementation and these technical choices remain proposed, not auto-accepted.

---
id: bf8d3c4f-8d01-4e66-9ff4-9413deffef78
type: implementation
status: proposed
parents:
- 1f2e42c3-331f-4c1c-adc7-897f9bf2e004
- 2b6a0e4e-f07f-4932-b58b-40348d4c3ac1
- 2b8a4bbc-d15a-4347-90b4-691abdeefaef
- 51c3e963-674e-4d5d-bd7a-b8d63649e1c8
- adb5a4c8-f9c5-4bcc-b38b-8584d469cf25
- fbaee7c1-4c20-47ab-afd2-ae0503d428b5
- d70cdad5-5e03-4200-ac75-74cf6514e56c
sources:
- path: docs/node-canvas.md
- path: vscode/.vscodeignore
- path: vscode/media/graph-camera.js
  symbol: createCamera
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
- path: vscode/LICENSE
managed_hash: a1438fe0bc0a2170345c285754353e72fe47a4bade973239722d9e387514b615
---
# Display, navigate, edit, and compare graphs through the CLI

The extension host launches the Python JSON CLI with bounded, shell-free processes.
The nonce-protected local webview renders an overview or focused neighborhood;
the same native form DOM moves into the expanded selected node. Managed writes,
actual parent links/candidate choices, explicit acceptance/retirement, workspace
trust, read-only history, stale-fingerprint drafts, Git overlays, startup logs,
and token-matched complete-render checks remain separate from presentation.

Dagre receives stably ordered node IDs/relations and intrinsic card dimensions in
LR mode. No viewport size enters arrangement. Compact and expanded widths are
fixed world sizes; the expanded height is measured without its camera scale.
Unchanged layout inputs are cached. Resizing a form relayouts geometry while
keeping the focused card's screen anchor and existing input/caret. Window resizing
clips the same world rather than wrapping or silently reframing its nodes.

D3 shape generates horizontally tangent Bezier connections at right output and
left input sockets. Dagre's skipped-rank lanes are retained across full card-width
bands before smoothing the gaps; otherwise a spline can average away clearance
and cut through cards. Historical reverse links loop outside their columns with
removed-edge patterns. Git strokes/badges are separate from status/distance fills.

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

Verification includes TypeScript compilation and bridge/activation/DOM/model tests
for layout determinism, LR constraints, obstacle corridors, cyclic overlays,
viewport invariance, pointer zoom anchoring, unconstrained drag, zoom bounds,
keyboard controls, independent cameras, caret/draft preservation, and existing
trust/history/injection restrictions. Installed VS Code/Chromium on Windows has
rendered the current 42-node graph, sampled curves for content intersections,
verified scaled/resized side-port geometry, navigated focused views and back,
panned/zoomed, narrowed the viewport without reflow, retained native form gestures,
and switched color modes. Screenshots were captured and visually inspected.
Full manual mutation/review and revision-picker verification remain outstanding.
Synchronous layout and full DOM rendering are not large-graph virtualization.

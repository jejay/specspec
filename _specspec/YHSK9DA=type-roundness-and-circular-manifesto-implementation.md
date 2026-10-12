---
id: YHSK9DA=
type: implementation
parents:
- AZbsoEA=
sources:
- path: graph-ui-common/media/graph.css
  symbol: type radii, circular manifesto content and marker placement
- path: graph-ui-common/media/graph.js
  symbol: applyLayout measured circular native editor
- path: graph-ui-common/media/graph-model.js
  symbol: manifestoDiameter, sideBoundary and shape-aware routeEdges
- path: graph-ui-common/test/graph-model.test.cjs
  symbol: circle fit, ports, minimum-zoom departure and reverse tests
- path: graph-ui-common/test/graph.test.cjs
  symbol: compact/expanded type radii, circular size/caret/draft/color regressions
- path: graph-ui-common/test-host/ui.cjs
  symbol: real type/content/marker fit, grow/shrink and shape-aware collision/endpoint checks
- path: tools/rainbow-playground/index.html
  symbol: circular neutral manifesto sample
- path: graph-ui-common/test/playground.test.cjs
  symbol: sample circle and unchanged exports
- path: graph-ui-common/test-host/playground.cjs
  symbol: real circular sample fit
- path: docs/node-canvas.md
  symbol: shape/footprint rationale
- path: docs/own-spec.md
  symbol: type roundness and circular manifesto
---
## Later zero-radius correction

ejSVfuc= sets Implementation corners to 0px, compact and expanded. The 7px
choice and actual checks below describe the initial shape implementation, not
current Implementation roundness. Requirement/circle/content/route choices remain
in scope; new checks belong to the later zero-radius evidence record.

# Render sharper implementations, rounder requirements and a true circular manifesto

Implement Dn6Ult8= through AZbsoEA= in the shared renderer for both hosts. CSS now
uses Implementation radius 7px (former Requirement), Requirement 24px (slightly
more than former Implementation 20px), and manifesto radius 50%. Remove generic
expanded radius 8px so each type retains its own outline in editing mode.

Keep ordinary compact cards 264 by 112 and ordinary expanded cards 860 wide.
Compact manifesto cards are 264 square, with centered/inset content and a Git
marker inside their lower-right arc. Expanded manifesto cards keep the same native
form DOM at its prior 822px content width, measure its intrinsic height and choose
a square diameter ceil(hypot(content width, content height)+48). Center the native
form, retain visible controls/80-column budget, and recalculate when ResizeObserver
reports form/textarea resize. The circle can be much larger than a rectangle;
this is the explicit shape-versus-footprint tradeoff, not a viewport-based layout,
changed font, cropped form, pill, or a silently rectangular expanded root.
A 720-height fallback is used only when the DOM environment cannot measure layout.

Carry shape/radius in transient layout sizes/positions, not nodes, drafts, camera
preferences or persisted host state. Pure sideBoundary calculates circle/rounded
rectangle chords at distributed port heights. Preserve 3-unit endpoint clearance,
minimum screen ink/head strength and horizontal tangent joins. Circle ports span
its middle 40% vertically so even thick minimum-zoom departure ink stays outside
the curved border. Rectangular forms keep full-height attachments. Flat launch/
settling segments clear conservative bounding boxes before curves turn; Dagre and
obstacle corridors still use those boxes. Existing reverse/history routes remain
finite and directed. Do not change production camera logic or native form identity.

Seven base colors, Requirement color 5/Added color 4, all other roles, distance
cycle, tints, themed titles/letters/edges, root white-versus-colored hover and
renderer-only labels remain unchanged. The offline playground gray manifesto
sample also uses a 150px circle; parameters/mappings/exports and other distance
samples are unchanged. No backend/schema/protocol or maintained history rewrite.

Unit regressions check circle diagonal breathing room, corner/chord ports, retained
shape layout data, clear bounding-box leads, reverse routes and minimum-zoom ink.
DOM checks verify all three compact/expanded radii, square circular boxes, exact
native form budget, measured growth/shrink, colors, form identity/caret/draft.
Update the three old all-card dimension assertions to the deliberate circle
exception rather than removing checks. The initial common run failed only those
obsolete size assertions; the revised suite passes all 131 tests. All earlier
hover/label/no-persistence/native geometry invariants remain checked.

Real-host checks independently verify computed type radii, square/50%-radius root,
content rectangle/marker corners inside its circle, formula-derived diameter,
exact 822px form width, grow/shrink on native textarea resize, 80-column text at
13/14/16px, visible Implementation expansion, real arc endpoints and finite clear
routes. Collision tests now use actual circular/rounded outlines instead of
mistaking transparent bounding-box corners for card content; curve/head tangent,
minimum-strength and native editing/camera/label assertions remain intact.

Actual local Windows checks passed: 131 common UI, 34 VS Code adapter, nine Electron
and 111 Python tests; Ruff lint/format; working graph and example snapshot validators
with warnings as errors. Standalone file:// browser checks pass with a circular
sample and unchanged exports. Electron build and its complete direct host runner
passed twice; the first combined screenshot filter matched no names, so a single
node-shapes filter on the unchanged assertion suite captured compact/expanded
Implementation/expanded manifesto images in the second run. Full direct VS Code
host checks passed with root screenshots after explicit compilation. Inspected
Electron compact/type/expanded-circle, VS Code expanded-root and playground
screenshots. Logs/images remain ignored local evidence, not cross-platform or
arbitrary display/graph/accessibility certification. No test timeout/assertion
was weakened and no hook was installed.

Refresh README, technical conclusion, canvas rationale and own-spec entry points;
mark earlier universal card dimensions/checks as history. Existing unrelated
fixture/history/workspace-policy work was present during verification and stays
outside this shape slice. Stage only intended graph/code/docs and validate the
exact index before committing separately from the shape specification.

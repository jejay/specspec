---
id: 8Slagkc=
type: implementation
parents:
- JVHv1gc=
sources:
- path: graph-ui-common/media/graph-model.js
- path: graph-ui-common/media/graph.js
- path: graph-ui-common/media/graph.css
- path: graph-ui-common/view.cjs
- path: graph-ui-common/test/influence.test.cjs
- path: graph-ui-common/test/graph.test.cjs
- path: graph-ui-common/test-host/ui.cjs
- path: docs/own-spec.md
- path: docs/node-canvas.md
- path: docs/graph-structure.md
---
# Render continuous absolute and cohort-relative influence

The shared graph model reuses iterative, deduplicated descendant traversal and
per-revision maximum distances. Lazy raw normalization ranges feed linear or
log1p normalization and the continuous three-anchor sRGB ramp. The shared template
exposes all four influence modes; the renderer uses target/base context, concise
continuous legends and persistent per-view mode selection. Scaling formulas live
in the tutorial. Compact and
expanded cards share normalization. Neutral drafts, manifesto treatment and existing
Git/highlight/form/camera roles stay independent.

Pure tests cover shared descendants, absolute zero-based normalization, cohorts by
longest path, positive cohort minima, log1p before normalization, ties, invalid
inputs, order invariance and interpolation. DOM tests cover focus, independent
base/target versions, refreshed ranges, all four preferences and preservation of
drafts, caret, geometry and camera. The common real-host probe checks all four
influence modes against independent full-revision graph traversals and transformed
count/cohort calculations, alongside actual gradient paint and persisted selection.

The graph-structure guide records installed-host phase boundaries and verification
limits alongside the model/DOM and adapter evidence.

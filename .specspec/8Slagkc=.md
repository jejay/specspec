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
---
# Compute and paint the four influence modes on a continuous ramp

`metrics` in `graph-ui-common/media/graph-model.js` counts the descendants of a node iteratively, each of them once, and takes the maximum distances of the same revision. `influence` includes the node itself, and `descendantCount`, the structural count that the cards show, is one less. `influenceRatio` builds the ranges of the raw counts on first use and normalizes either the influence minus one or its natural logarithm, and `influenceColor` maps the result onto the continuous ramp of three sRGB anchors. The template in `graph-ui-common/view.cjs` offers all four influence modes. The renderer in `graph-ui-common/media/graph.js` takes the values of a node from the target or from the base of a comparison, draws a short continuous legend, which `graph-ui-common/media/graph.css` sizes, and stores the selected mode for each view. Compact and expanded cards share the normalization. A draft is neutral, the manifesto is gray, and the Git marks, the highlights, the form and the camera work independently of the influence modes.

The unit tests in `graph-ui-common/test/influence.test.cjs` cover descendants that several paths share, influence that includes the node itself, the linear normalization, the groups by longest path, a group with a positive minimum, the logarithm before the normalization, ties, invalid input, independence of the order of the input and the interpolation of the ramp. The DOM tests in `graph-ui-common/test/graph.test.cjs` cover the view of a selected node, separate values for the base and the target, ranges that are refreshed, all four stored preferences and that drafts, the text cursor, the geometry and the camera stay as they are. The probe in `graph-ui-common/test-host/ui.cjs`, which both installed editors run, checks all four modes against a traversal of the complete revision and a calculation of the transformed counts and groups that are written independently of the model, together with the painted gradient and the stored selection.

The complete suites in the installed editors combine every mode with source previews, editing in the form, spotlights, recovery and the checks of reloads and revisions.

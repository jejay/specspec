---
id: YHSK9DA=
type: implementation
parents:
- AZbsoEA=
sources:
- path: graph-ui-common/media/graph.css
- path: graph-ui-common/media/graph.js
- path: graph-ui-common/media/graph-model.js
- path: graph-ui-common/test/graph-model.test.cjs
- path: graph-ui-common/test/graph.test.cjs
- path: graph-ui-common/test-host/ui.cjs
- path: tools/rainbow-playground/index.html
- path: graph-ui-common/test/playground.test.cjs
- path: graph-ui-common/test-host/playground.cjs
---
# Render square implementation cards, rounded requirement cards and a circular manifesto

`graph-ui-common/media/graph.css` sets a radius of 0px for an implementation, 24px for a requirement and 50% for the manifesto, compact and expanded. An ordinary card is 264×112 and 860 wide when expanded, and the compact manifesto is 264×264. `applyLayout` in `graph.js` measures the same form at 822px of content width and sizes the expanded circle with `manifestoDiameter = ceil(hypot(width, height) + 48)` from `graph-model.js`. When the form changes its size, the footprint follows, and the editor, the text cursor and the camera stay as they are.

`sideBoundary` and `routeEdges` in `graph-model.js` attach the links to the actual outlines with 3 units of clearance, to the chords of a circle within the middle 40% of its height and to ports along the full height of an ordinary card, and they lead a link straight out and straight in before it turns. Conservative bounding boxes supply the corridors. The sample of a manifesto in the palette playground, `tools/rainbow-playground/index.html`, is a circle of 150px.

The tests of the pure model, of the DOM and in the installed editors check the radii of the types, the diameter formula, that content and Git marker fit, growth and shrinking after a measurement, links drawn against the direction of the layout, the painted clearance and the fields of the form. The collision checks, written independently of the routing, treat the interior of a square card with radius 0 and of an actual circle explicitly. The palette, the state of the labels and the logical relationships are the same whatever the shape.

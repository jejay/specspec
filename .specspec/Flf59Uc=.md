---
id: Flf59Uc=
type: implementation
parents:
- 6QB9hRY=
sources:
- path: graph-ui-common/media/graph-model.js
- path: graph-ui-common/media/graph.js
- path: graph-ui-common/media/graph.css
- path: graph-ui-common/view.cjs
- path: graph-ui-common/test/rainbow.test.cjs
- path: graph-ui-common/test/graph.test.cjs
- path: graph-ui-common/test-host/platform.cjs
- path: graph-ui-common/test-host/ui.cjs
- path: tools/rainbow-playground/palette.js
- path: tools/rainbow-playground/index.html
- path: graph-ui-common/test/playground.test.cjs
- path: graph-ui-common/test-host/playground.cjs
---
# Fill cards from the seven exact colors by distance, type and comparison kind

`graph-ui-common/media/graph-model.js` exports the exact `RAINBOW_COLORS`, the neutral color, the maps for types and for revision kinds, the labels and the modes. A requirement is entry 4 and an added node entry 3, an implementation 0, a modified node 1, a deleted node 6 and a node with changed sources alone 5. A distance `d` takes `(d-1)%7`, and an unknown or neutral state is gray. The renderer in `graph.js` derives the revision kind of a node from the selected comparison before the impact of sources and applies it alike to compact cards, expanded cards and the manifesto.

The template in `graph-ui-common/view.cjs` offers the modes, the view stores the selected mode as a preference, and the legend shows the colors in use. The form with its text cursor, the camera, the geometry and the separate Git cues of headline and links are the same after a switch of the mode. `graph-ui-common/test/rainbow.test.cjs` and the other linked tests compare the literal bytes of the colors and the mappings, an independent conversion to OKLCH, the wrap of the cycle, the behavior of the manifesto, of types, of statuses, of a view without a comparison and of drafts, and that the defaults of the playground export exactly these values.

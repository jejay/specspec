---
id: NsFLK9o=
type: requirement
parents:
- mAZgRy8=
---
# Let the browser rasterize the text of the cards at the current zoom level

The headlines and the forms of the cards are ordinary DOM elements under the two-dimensional transform of the camera, and the browser rasterizes them at the current scale. The logical font sizes, the sizes in world units, the rendering of text through `textContent`, the measured sizes of the cards and the form elements themselves are the same at every scale. The transformed graph has the default `will-change: auto`, so the browser composites it by its normal rules.

A probe in the installed editors zooms a headline to 250% and inspects it once the picture has settled, at one and the same camera position with and without a layer hint. The checks of navigation, routing, the form with its text cursor and the paint at low zoom run alongside. What these checks prove is limited to the browser, the operating system, the fonts and the device they ran on.

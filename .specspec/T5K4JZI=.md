---
id: T5K4JZI=
type: implementation
parents:
- bLBNk80=
sources:
- path: graph-ui-common/media/graph.css
- path: graph-ui-common/test/graph.test.cjs
- path: graph-ui-common/test-host/ui.cjs
- path: README.md
---
# Derive the hover paint of colored cards and incident links in their own hue

`graph-ui-common/media/graph.css` derives the border of a hovered colored card and the ink of incident added, removed and draft links in OKLCH from their own color: lightness plus 0.10 up to 0.95, chroma times 1.30 and the same hue. The border of the gray manifesto of the distance and type modes is white on hover, and a manifesto colored by revision status takes its own hue. A neutral ordinary link mixes its color with the foreground color of the theme, and the darkening of unrelated cards and links has its own membership and its own ink.

The tests convert the colors that the browser actually computed to OKLCH and check that the result is lighter, more saturated and of the same hue, that exactly the incident pairs are emphasized and restored, and that width, dashes, routes, head geometry and the form are the same throughout. These checks hold for the editors and themes that were probed, within the gamut mapping of the browser and the conditions of the display.

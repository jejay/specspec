---
id: yCYr-E0=
type: requirement
parents:
- u8tHkaE=
- 2XVN2Jo=
---
# Scale neutral arrow ink from seventy to thirty-five percent with zoom

The ink of an ordinary link, on its curve and on its arrowhead, is the neutral link color of the theme mixed with black. At camera scales of 70% and above the mix holds 70% of the neutral color. Below that the share falls linearly to 35% at a scale of 16%, and it is 35% at every smaller scale: `strength = 0.35 + 0.35 * clamp((scale - 0.16) / (0.70 - 0.16), 0, 1)`. An invalid scale counts as actual size. Curve and arrowhead carry the same ink at full opacity, and the minimum sizes on screen and the geometry of the routes are independent of the ink.

The camera sets one inherited CSS property, `--normal-edge-strength`, and the ink of ordinary links alone uses it. The hover emphasis of an ordinary link mixes the undimmed neutral color of the theme with the foreground color of the theme, whatever the zoom level. Added, removed and draft links follow their own rules for an emphasis in their hue, and the darkening of the links that do not touch a hovered card is a separate treatment. These constants are settings of the paint and belong to the presentation, apart from the data of the graph and its nodes.

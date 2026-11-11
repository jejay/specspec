---
id: eqWEPJI=
type: requirement
parents:
- sV3uzvQ=
- yCYr-E0=
---
# Blend the fill of a card into its painted border between camera scales of 40% and 16%

The background of a card changes between camera scales of 40% and 16%: `q = 1 - clamp((scale - 0.16) / (0.40 - 0.16), 0, 1)`, and an invalid scale counts as actual size. At 40% and above the background is the fill of actual size, and below that it grows stronger toward the border as the graph is zoomed out. The ink of ordinary links has a range of its own, from 70% to 16%. The two treatments begin at different scales and both reach their end at 16%.

The fill of actual size is the canvas background of the theme mixed with 15% of the accent color that carries the color meaning, or with 24% on hover. This fill is then mixed toward the border as it is currently painted, by the share `q`. For a card at rest the accent thus has a strength of `0.15 + 0.85 * q`. A hovered card has its tint of 24% at actual size and reaches its emphasized border at the far end of the range. In a high-contrast theme the base is the theme background alone, and the border is the contrast border of the theme or, where the theme defines none, the foreground color of the surrounding editor.

At a scale of 16% and below every fill equals its visible border, including the white border of the hovered neutral manifesto and the borders of the high-contrast themes. At actual size and above, the tints and the text are exactly those made for editing. The darkening on hover and the rings of a spotlight are painted independently of the fill. The camera updates one inherited CSS property for the progress of the fill, `--node-fill-strength`, on the cards that are drawn, alongside the paint of the links and independently of it, and the inputs and the positions in the world stay as they are. Mixing in two stages keeps both the hover tint at actual size and the border as the end point.

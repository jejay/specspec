---
id: yCYr-E0=
type: requirement
parents:
- u8tHkaE=
- 2XVN2Jo=
---
# Scale neutral arrow ink from seventy to thirty-five percent with zoom

For normal curve/head pairs, mix theme neutral ink with black at 70% ink at camera
scales of 70% and above. Decrease that proportion linearly to 35% at 16% scale
and below:
strength = 0.35 + 0.35 * clamp((scale - 0.16) / (0.70 - 0.16), 0, 1).
Treat invalid scales as actual size. Apply the same ink at full opacity to the
existing curve and head, retaining minimum screen dimensions and all route geometry.

The camera sets one inherited normal-edge-strength property; only ordinary ink
uses it. Normal incident-hover paint mixes original theme neutral/foreground ink,
independently of the zoom dimming. Added/removed/draft colors keep their hue-emphasis
rules. Non-incident hover darkening retains its separate context treatment. These
bounded paint constants are revisable visual choices, not graph or node metadata.

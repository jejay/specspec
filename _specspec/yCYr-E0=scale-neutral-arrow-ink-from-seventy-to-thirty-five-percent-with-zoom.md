---
id: yCYr-E0=
type: requirement
parents:
- u8tHkaE=
- 2XVN2Jo=
---
# Scale neutral arrow ink from seventy to thirty-five percent with zoom

For normal curve/head pairs, mix theme neutral ink with black at 70% ink at actual
size and above. Decrease that proportion linearly to 35% at the 12% camera limit:
strength = 0.35 + 0.35 * clamp((scale - 0.12) / 0.88, 0, 1). Clamp lower inputs to
the minimum and treat invalid scales as actual size. Apply the same ink at full
opacity to the existing curve and head, retaining minimum screen dimensions and
all route geometry.

The camera sets one inherited normal-edge-strength property; only ordinary ink
uses it. Normal incident-hover paint mixes original theme neutral/foreground ink,
independently of the zoom dimming. Added/removed/draft colors keep their hue-emphasis
rules. Non-incident hover darkening retains its separate context treatment. These
bounded paint constants are revisable visual choices, not graph or node metadata.

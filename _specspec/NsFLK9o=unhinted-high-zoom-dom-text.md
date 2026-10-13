---
id: NsFLK9o=
type: requirement
parents:
- XzlIEcQ=
- mAZgRy8=
- bOXyw00=
---
# Rasterize native text at the current camera scale

Use ordinary native DOM headlines/forms with the shared two-dimensional camera
transform and browser rasterization at the current scale. Keep logical fonts, world
sizes, textContent rendering, intrinsic measurements and native editing identity.
The world uses normal compositor decisions rather than a permanent transform-layer
promotion hint. Inspect settled high-zoom text with matched poses and keep low-zoom
navigation, routing, form/caret and paint checks. Rendering evidence is scoped to
browser, OS, fonts and device conditions.

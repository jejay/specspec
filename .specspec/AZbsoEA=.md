---
id: AZbsoEA=
type: requirement
parents:
- xCOHepQ=
- ejSVfuc=
---
# Draw implementation cards square, requirement cards rounded and the manifesto as a true circle

An implementation card has corners of 0px and a requirement card corners of 24px, compact and expanded. An ordinary compact card is 264×112, and an expanded one is 860 wide with the height of its content. The compact manifesto is 264×264 with a radius of 50%, and its content and its Git marker are centered and inset.

The expanded manifesto is a square with a radius of 50% that holds the same form as every other card, at 822px of content width. Its diameter is `ceil(hypot(822, intrinsicContentHeight) + 48)`. The form is centered, its intrinsic height is measured, and the diameter is computed again when the form or a textarea is resized. This footprint is a true circle with room for a typical line of 80 columns, and framing and panning bring its larger area in the world into view. A fallback for the measured height serves only tests that run without layout.

The routing of the links receives the shape and the radius of each card as transient data. The ports of a circle span the middle 40% of its height and lie on the chord of the circle at their height. The ports of a rounded card lie on its actual outline. An endpoint keeps 3 units of clearance, and a link leaves and arrives in a straight segment that clears the bounding box before it turns. Obstacles and corridors are computed from the conservative bounding boxes. A change of shape or footprint leaves the palette and the tints, the labels and the hover, the DOM of the form with its text cursor, the camera and the behavior of sources and references as they are.

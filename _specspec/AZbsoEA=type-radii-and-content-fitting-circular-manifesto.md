---
id: AZbsoEA=
type: requirement
parents:
- Dn6Ult8=
- xCOHepQ=
- qf5-4sc=
---
# Use type radii and fit the native manifesto editor inside a true circle

Use the former Requirement radius 7px for Implementation cards and increase the
former Implementation radius 20px to 24px for Requirement cards, in compact and
expanded states. Remove the generic expanded-radius override. Keep ordinary
compact cards 264 by 112 and ordinary expanded cards 860 wide with intrinsic height.

Make compact manifesto cards 264 by 264 with 50% radius, centered inset content
and a Git marker inside the lower-right arc, not the clipped bounding-box corner.
For expanded manifesto cards retain the prior native form's 822px content width
(860 minus padding/borders), measure its intrinsic height, and use a square outer
box whose diameter is the content rectangle diagonal plus 48px breathing room.
Center that same form DOM inside the circle; grow the circle on intrinsic form/
textarea resize. Do not silently revert an expanded manifesto to a rectangle,
clip controls, use a scroll-only tiny root form or reduce its 80-column text budget.
The larger circular outer footprint is a deliberate tradeoff for true-circle
editing; framing/panning remain available. A jsdom measurement fallback is only
for tests, not a different production layout.

Pass measured shape/radius data into pure layout/routing. Circle ports use the
circle chord at each distributed port height; rounded rectangles use the actual
corner boundary where needed. Retain the existing 3-unit endpoint clearance and
horizontal tangent/head joins. Departure/settling points clear the conservative
bounding boxes before curves turn, avoiding cutting into an arc. Use bounding
boxes conservatively for Dagre/corridor obstacles, without viewport-dependent
layout. Hover/labels must not change sizes, camera, routes or native fields.

Keep colors/mappings, tints, white-gray-root versus hue-preserving revision hover,
Git/withdrawal/source cues and renderer-only label preview unchanged. No canonical
schema, backend, host-domain fork or maintained example-history rewrite is needed.
Verify compact and expanded types, square/50%-radius manifesto, content/marker fit,
shape-aware endpoints, finite reversible routes, resize, native editing/80 columns,
unchanged label/hover geometry and actual Windows hosts. Pixel sizes/fit math are
revisable choices, not universal display/accessibility certification.

Circle ports span the middle 40% of their vertical arc, keeping even the thick
minimum-zoom departure stroke outside the curved border at the existing 3-unit
gap. Ordinary rectangular forms keep full-height port distribution. The standalone
playground also shows its gray manifesto sample as a 150px circle, without changing
parameters, swatches, mappings, exports or distance sample shapes.

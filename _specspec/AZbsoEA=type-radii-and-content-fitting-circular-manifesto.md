---
id: AZbsoEA=
type: requirement
parents:
- Dn6Ult8=
- qf5-4sc=
- xCOHepQ=
- ejSVfuc=
---
# Fit square and rounded cards plus a true circular manifesto

Use 0px Implementation and 24px Requirement corners in compact and expanded views.
Ordinary compact cards are 264×112; expanded width is 860 with intrinsic height.
Compact manifesto is 264×264 with 50% radius and centered inset content/Git marker.

Retain the same native form at 822px content width inside an expanded square/50%
root. Diameter is `ceil(hypot(822, intrinsicContentHeight) + 48)`. Center the form,
measure intrinsic height and recalculate on form/textarea resize. The footprint
provides a true circle and typical 80-column content budget; framing/panning exposes
its larger world area. A measurement fallback is confined to layout-less tests.

Pass transient shape/radius data to routing. Circular ports span middle 40% of
height and use chord boundaries. Rounded ports use their actual outline. Keep
3-unit endpoint clearance and straight bounding-box-clearing departure/settling
segments before turns; conservative boxes determine obstacles/corridors. Preserve
palette/tints, labels/hover, native DOM/caret, camera and source/reference behavior.

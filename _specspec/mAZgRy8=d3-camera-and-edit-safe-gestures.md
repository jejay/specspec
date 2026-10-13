---
id: mAZgRy8=
type: requirement
parents:
- LtROyww=
- XzlIEcQ=
- bOXyw00=
---
# Use a separate native-world D3 camera

Use d3-zoom for one transform over native DOM cards and SVG. Allow unconstrained
pan and bounded 12–250% magnification. Middle/background drag pans; wheel/pinch zooms
at the pointer. Buttons and keyboard actions frame graph/node or restore actual
size. Scale/framing uses viewport bounds; node arrangement uses world relationships.

Keep independent overview/focus cameras and original drafts in per-view state.
Back/refresh retain camera poses; explicit framing changes them. Honor reduced-motion
preferences. Native controls keep text selection, textarea scroll/resize, dropdown
and button gestures. Camera navigation updates presentation alone.

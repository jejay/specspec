---
id: mAZgRy8=
type: requirement
parents:
- LtROyww=
- XzlIEcQ=
- bOXyw00=
---
# Use a separate D3 camera for an unbounded editing surface

Reuse d3-zoom with one CSS transform for the DOM cards and their SVG connections.
The viewport clips the world; its size only affects camera framing, never node
arrangement. Keep finite bounded scale with unconstrained pan, pointer-anchored
wheel/pinch zoom, middle-button pan, background drag, and explicit zoom/frame
controls. Provide keyboard equivalents without stealing native text editing.

Preserve independent overview/focus camera state in the webview, alongside drafts
and their original node contents. Back restores the overview camera; refresh and
resizing must not silently refit or reset navigation. Explicit framing is a camera
action, not graph reflow. Adapt smooth transitions to reduced-motion preferences.

Exclude native form gestures from canvas navigation. Keep text selection, textarea
scrolling/resizing, dropdowns, buttons, and node activation usable. Pan/zoom must
not invoke the CLI or change canonical metadata. Test actual wheel/drag gestures,
geometry under scale, viewport-size invariance, and draft/revision regressions.

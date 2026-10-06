---
id: d70cdad5-5e03-4200-ac75-74cf6514e56c
type: requirement
parents:
- 18d1da0d-8bc3-4d58-8720-8ce194a74d1b
- a723adc8-d69d-4e60-8b4f-0997ab8f4d1d
- 2b8a4bbc-d15a-4347-90b4-691abdeefaef
managed_hash: c0dac805e887eeaf93899f0bc0947cb208b22b4a6f0ce2b75970ce31b2110f98
---
# Use a separate D3 camera for an unbounded editing surface

Reuse d3-zoom with one CSS transform for the DOM cards and their SVG connections.
The viewport clips the world; its size only affects camera framing, never node
arrangement. Keep finite bounded scale with unconstrained pan, pointer-anchored
wheel/pinch zoom, middle-button pan, background drag, and explicit zoom/frame
controls. Provide keyboard equivalents without stealing native text editing.

Preserve independent overview/focus camera state in the webview, alongside drafts
and their original fingerprints. Back restores the overview camera; refresh and
resizing must not silently refit or reset navigation. Explicit framing is a camera
action, not graph reflow. Adapt smooth transitions to reduced-motion preferences.

Exclude native form gestures from canvas navigation. Keep text selection, textarea
scrolling/resizing, dropdowns, buttons, and node activation usable. Pan/zoom must
not invoke the CLI or change canonical metadata. Test actual wheel/drag gestures,
geometry under scale, viewport-size invariance, and draft/revision regressions.

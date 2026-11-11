---
id: zwevPEc=
type: requirement
parents:
- FZO2_-Q=
- zs0OtME=
- mAZgRy8=
---
# Capture rectangle framing in viewport pixels and invert the starting camera

Use Ctrl on Windows/Linux and Command on macOS, preserving macOS Control-click.
Use the bare primary modifier, with Shift/Alt and other platform modifiers retaining
their existing gestures. An armed icon starts the same one-shot interaction. The
rubber band is a viewport overlay separate from the transformed world. Capture the
primary pointer and initial camera; invert both rectangle corners through that
camera and normalize their bounds. Frame with 40 CSS pixels of margin per side,
allowing up to the existing 250% camera maximum. Graph/node framing keeps its 100%
cap. Require at least four CSS pixels on both axes; smaller gestures complete with
the camera retained. A completed modifier gesture rearms after release and a fresh
modifier press. The icon can be toggled off or rearmed explicitly.

Pointer release outside the canvas completes through pointer capture/window release.
Escape, pointer cancellation, capture loss, blur and disposal clear the overlay and
cursor with the camera retained. Wheel, pan and camera keyboard shortcuts pause
while dragging. Consume the completed gesture's click so framing retains selection
and highlights. Native form/control/link targets keep their regular interactions.
Keep transient tool state in renderer memory. Verify both modifier mappings with
synthetic events; physical macOS behavior has its own qualification boundary.

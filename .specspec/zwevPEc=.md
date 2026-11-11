---
id: zwevPEc=
type: requirement
parents:
- FZO2_-Q=
- zs0OtME=
- mAZgRy8=
---
# Draw the framing rectangle in viewport pixels and convert it through the camera of the moment the drag began

The gesture uses the primary modifier key: Ctrl on Windows and Linux and Command on macOS, where Control-click has its own meaning. The modifier counts when it is held alone: with Shift, Alt or the other platform modifier held as well, those keys have their own gestures. The Frame rectangle icon arms the same one-shot tool, a click on the armed icon switches the tool off, and a further click arms it again. After a gesture that was completed with the modifier held, the tool arms again once the modifier has been released and pressed anew.

The rectangle is an overlay in the coordinates of the viewport, apart from the transformed graph. A press captures the primary pointer and records the camera of that moment. On release both corners of the rectangle are converted through the inverse of that camera into world coordinates and ordered into bounds, whatever the direction of the drag. The camera frames these bounds with a margin of 40 CSS pixels on each side and zooms in up to its maximum of 250%, while framing the graph or a node zooms in to 100% at most. A rectangle needs at least four CSS pixels on both axes, and a smaller gesture completes the tool and leaves the camera where it is.

A release outside the canvas completes the gesture, through the pointer capture and a listener on the window. Escape, a cancelled pointer, a lost capture, a window that loses focus and the disposal of the camera remove the overlay and the crosshair and leave the camera where it is. While a rectangle is dragged, the wheel, panning and the keyboard shortcuts of the camera pause. The click that follows a completed gesture is consumed, so that framing changes neither the selection nor the highlights. A press on a form, a control or a link acts as it does without the tool. The state of the tool lives in the memory of the renderer alone. Tests verify both modifier mappings with synthetic events, and the behavior on a physical Mac is outside these checks.

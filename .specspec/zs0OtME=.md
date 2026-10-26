---
id: zs0OtME=
type: requirement
parents:
- XzlIEcQ=
---
# Frame a drawn rectangle with a one-shot canvas tool

Offer a framing icon and a primary modifier gesture to draw a visible rectangle
and frame its world-space area. Hover with the modifier shows a crosshair. Releasing
the modifier before pressing returns the ordinary cursor. Primary press starts the
rectangle at that point; movement updates it in every direction. Once dragging,
the rectangle and crosshair stay active through modifier release. Pointer release
frames the area regardless of modifier state and completes the tool.

Keep native controls, links, caret, drafts, ordinary selection/panning, context menus
and Shift highlight gestures usable. Cancellation clears the transient tool while
retaining the current camera. Keep world geometry and canonical data independent.

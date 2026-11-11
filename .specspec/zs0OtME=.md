---
id: zs0OtME=
type: requirement
parents:
- XzlIEcQ=
---
# Frame a drawn rectangle with a one-shot canvas tool

A framing icon and a gesture with the primary modifier key let the owner draw a visible rectangle and frame the area of the graph world that it covers. Hovering with the modifier held shows a crosshair, and releasing the modifier before pressing brings the ordinary cursor back. A press of the primary button starts the rectangle at that point, and moving the pointer updates it in every direction. Once the drag has begun, rectangle and crosshair stay active when the modifier is released. Releasing the pointer frames the area whatever the state of the modifier and completes the tool.

Controls, links, the text cursor, drafts, ordinary selection and panning, context menus and the Shift gestures for highlights stay usable. Cancelling removes the transient tool and keeps the current camera. The tool leaves the geometry of the world and the node files untouched.

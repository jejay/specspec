---
id: -0ljwrM=
type: requirement
parents:
- qf5-4sc=
- XzlIEcQ=
- SRsw2W0=
---
# Emphasize the links of the hovered card from pointer state kept in the renderer

The viewport receives the pointer events of devices that can hover and derives from them which card the pointer is over. The renderer keeps the ID of the hovered card and the last pointer position in its memory. The emphasis stays while the pointer moves among the controls inside one card. It ends when the pointer leaves, the window loses focus, the pointer is cancelled or a touch arrives. After a redraw and after a camera movement the renderer tests again which actual card lies under the last pointer position.

The emphasized links are those that the view draws between the hovered card and a direct parent or child, matched by their IDs, including the links of an earlier revision and the links of a draft. The renderer toggles classes on the existing pairs of curve and arrowhead and paints the incident pairs last. An ordinary neutral link takes an ink mixed from its own color and the foreground color of the theme, and a colored link is emphasized in its own hue. When the hover ends, the pairs return to their order and their paint. A hover changes paint and paint order alone: the geometry, the dash patterns, the positions in the world, the camera and the fields of the form are the same during and after it. The SVG of the links takes no pointer events, and the controls inside a card receive their events as in any form.

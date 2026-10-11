---
id: e3494686-5da4-40f5-a622-f823c2e0c9b2
type: requirement
parents:
- adb5a4c8-f9c5-4bcc-b38b-8584d469cf25
- 4d1f2eee-8125-4e3f-b9b4-649517875d87
---
# Draw clearly connected and directional relationship arrows

Relationship arrows must visibly connect the correct node boundaries and make
the direction of each link understandable, without running through node content.
Maintain readability when parents occupy different distances from the root.
Prefer smooth curved connections, as in a spatial node editor, over angular
orthogonal links; the chosen routing mechanism must still make endpoints clear.

Connections retain a minimum visible stroke strength even as nodes become smaller
when zooming out. Do not decorate endpoints with round connector circles. Arrowheads
must continue the approaching line naturally, including strongly curved links,
without an abrupt directional kink or a stroke protruding through the arrow tip.

Hovering a node also highlights all its displayed incoming and outgoing connection
curves and arrowheads, so users can trace its immediate relationships without
selecting or editing it. Apply this in overview and focused neighborhoods, including
expanded cards. Leaving the node removes the temporary emphasis. Preserve clear
direction and distinguish Git relationship changes while highlighting.

Origin: the user's node-hover request and initial arrow correction, Blender-like editor request, and
subsequent minimum-strength/no-circles/arrow-transition feedback in this conversation.
Screenshots illustrate defects, not a required algorithm, pixel size, or library.

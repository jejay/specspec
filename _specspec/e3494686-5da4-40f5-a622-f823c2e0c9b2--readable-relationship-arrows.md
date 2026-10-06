---
id: e3494686-5da4-40f5-a622-f823c2e0c9b2
type: requirement
parents:
- adb5a4c8-f9c5-4bcc-b38b-8584d469cf25
- 4d1f2eee-8125-4e3f-b9b4-649517875d87
managed_hash: 52a27fe471c315802f341edd6a66c2eca48b38c6cdabf0c0cfb1b5ac4b72aa8c
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

Origin: the user's initial arrow correction, Blender-like editor request, and
subsequent minimum-strength/no-circles/arrow-transition feedback in this conversation.
Screenshots illustrate defects, not a required algorithm, pixel size, or library.

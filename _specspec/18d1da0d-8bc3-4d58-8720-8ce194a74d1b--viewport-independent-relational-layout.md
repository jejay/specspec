---
id: 18d1da0d-8bc3-4d58-8720-8ce194a74d1b
type: requirement
parents:
- adb5a4c8-f9c5-4bcc-b38b-8584d469cf25
- 48f77f19-391f-46d0-b06f-ec7530be4575
---
# Let relationships determine a graph beyond the viewport

Derive node arrangement from logical relationships and sensible graph presentation,
not from the dimensions or borders of the editor window. Narrowing or enlarging
an area must not wrap, squeeze, or reorganize the graph to fit that area.

Graph content that does not fit is clipped behind the viewport boundaries and
remains available through navigation. View framing and magnification may change
without changing the underlying relational arrangement. This applies to focused
editing as well as the total graph.

Origin: the user's Blender-like node-editor request in this conversation.
Library, algorithm, and gesture-binding choices are separate technical conclusions.

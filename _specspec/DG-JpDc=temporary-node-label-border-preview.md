---
id: DG-JpDc=
type: requirement
parents:
- t8RQMdE=
- PL1IogE=
---
# Try colored node labels without persistence

Right-click a graph node to cycle no label -> red -> blue -> green -> purple ->
turquoise -> yellow -> no label. Show the label as a thick equal border around
the node, including overview/expanded and shared-host presentations. This first
step is a visual experiment only: do not save label information through the CLI,
canonical files or filesystem. Label persistence will likely be explored later,
but is not implemented or required in this slice.

Origin: the user's label test visualization request. Rendering, native-control
exceptions and transient view lifetime are separately revisable choices.

---
id: zOX2L9c=
type: requirement
parents:
- 7woeTpk=
---
# Color absolute and relative influence continuously

Influence counts the node itself plus its unique direct and indirect descendants,
with a minimum of one. Shared descendants contribute once per node, regardless of
how many paths reach them. Offer Absolute influence and Relative influence as
Color by options on a continuous Turbo-like red, yellow and green spectrum from
strongest to weakest, with blue outside the spectrum.

Absolute influence normalizes influence minus one from green to the highest
non-manifesto influence minus one at red. Leaf requirements and terminal
implementations have influence one and green accents. Relative influence compares
nodes with the same maximum directed distance from the manifesto, normalizing the
lowest influence to green and the highest to red. Structural downstream counts
report descendants excluding self.

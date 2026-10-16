---
id: zOX2L9c=
type: requirement
parents:
- 7woeTpk=
---
# Color absolute and relative influence continuously

Influence is the number of unique direct and indirect descendants, excluding the
node itself. Offer Absolute influence and Relative influence as additional Color by
options. Both use a continuous Turbo-like red, yellow and green spectrum, from
strongest to weakest influence, with blue outside the spectrum.

Absolute influence normalizes linearly from zero descendants at green to the
highest non-manifesto descendant count at red. Leaf requirements and terminal
implementations therefore have zero absolute influence and green accents.

Relative influence compares nodes only with others having the same maximum
directed distance from the manifesto. Within each such group, linearly normalize
the lowest descendant count to green and the highest to red. Shared descendants
contribute once per node, regardless of the number of paths reaching them.

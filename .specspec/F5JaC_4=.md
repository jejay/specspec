---
id: F5JaC_4=
type: requirement
parents:
- _yahyM4=
---
# Give every node a compact random ID that is written in full everywhere

A node ID has eight characters: seven Base64url symbols followed by one `=`, the standard padding sign. A new ID is made from random bytes, and it is made again when it collides with an ID in the project. The `=` belongs to the ID wherever the ID appears: in frontmatter, in parent lists, in commands, in API messages, in file names and in the graph editors. The name of a node file therefore ends in `=.md`.

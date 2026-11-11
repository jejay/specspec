---
id: _yahyM4=
type: requirement
parents:
- _wJJQko=
---
# Name each node file by the stable full ID of its node

Every reference to a node uses its full ID. The file of a node is named exactly `<id>.md`, with the closing `=` of the ID directly before `.md`. The file has YAML frontmatter, which states the ID, the type and the IDs of the parents, and a Markdown body, which holds the text of the node. What a person reads, the heading and the text, is inside the document, and the file name carries the ID alone. Editing the body or the parents changes neither the ID nor the path.

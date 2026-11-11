---
id: qSK7qA0=
type: requirement
parents:
- PAkzXxk=
---
# Offer a repair form for an editor document that cannot be parsed, apart from the nodes of the graph

A node document that is open in VS Code and whose header is recognized as the current format supplies the fields of a form, within the size limit and identified by its ID, also when an empty body or half-typed source JSON keeps the document from being parsed as a node. These fields are those of the actual document, with its unsaved text laid over the file, and they are returned apart from the nodes of the snapshot. The source input is kept literally, and the editor document stays the owner of its text and its version. The view stays editable for the repair and shows the fields that the document has at that moment, and the document counts as a node of the graph once it parses. Deleting a node and capturing a source need a target that the graph identifies as a node.

A repair form is offered only for a document that exists directly in `.specspec`, whose ID matches its file name, whose type is known and whose parents are written in usable syntax. A document in an unsupported format version, with a malformed ID or with unusable YAML is reached through its raw Markdown. The format version of the manifesto is recognized from its header whatever the state of its body. The checks of the writer on node documents, the guards on bytes and IDs, undo in VS Code and the rule that an absent file is never created from an open buffer apply to a repair as to every other edit.

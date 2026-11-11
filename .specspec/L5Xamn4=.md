---
id: L5Xamn4=
type: requirement
parents:
- -RQn7Ug=
---
# Keep declared links readable in an invalid graph and give context for a repair

The inventory of the files is kept apart from the parsed node records. A reference that does not resolve is told apart by its cause: the endpoint is absent, unreadable or ambiguous. The parents that a node declares are available as written, independently of the links that could be resolved for traversal. Diagnostics describe input in the current node format. A graph in another format version is reported as unsupported, and a raw read returns its documents exactly as they are.

`query --raw` reads a node document as it is, whatever errors the graph has, from the saved files, from the index or from a commit. `query --issues` works on the parsed nodes: it selects the nodes with faults of structure and the nodes beneath them that may be affected, and it adds their complete ancestors on request. Walks through the graph are safe against cycles and include the components that the manifesto does not reach. A metric is computed from the relationships that are known. Where the scope is unavailable, or a longest path would run through a cycle, the query fails with an explicit error and selects nothing.

A full `diff` compares the declarations and the bytes of the node files. It tells three cases apart: a file that was removed, a reference that was edited and a reference that stopped resolving. `--with-context`, with `--node` once or several times to choose nodes, adds the earlier and the current text and links, the ancestors that survive, the changes that were observed, one cause path for each cause and node, which is the same on every run, and a statement of what is unavailable. Context that several nodes share appears once. A limit on the bytes of the output fails the command before any part of the output is written.

An invalid graph alone leaves a complete comparison of the structure complete and says nothing about what the owner intends. Outside a Git repository a read with context returns what the current files show and patches against an empty inventory, labeled as such, as an incomplete comparison whose changes are reported as unavailable. A spotlight can name a node by the ID of its file while the graph is invalid, and the drift of the literal bytes is tracked whether or not the node parses.

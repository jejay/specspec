---
id: aILBxDs=
type: requirement
parents:
- 2FfVd-Y=
- 7tMgRa8=
---
# Read parsed nodes and raw node files through query alone

`query` is the one top-level command that reads the specification. `query ID` selects the node and its descendants, `--max-distance 0` reads the selected node alone, and `--with-ancestors` adds the ancestors that are its reasons. The comparison of revisions, the selection by distance and influence, `--issues`, the human presentation and the JSON form are options of this same command.

`query --raw` reads the literal text of a node file, selected by ID or with `--path`. With `--target` it reads the file of a committed revision, and with `--staged` the exact bytes of the Git index. `--path` and `--staged` are accepted with `--raw` alone. A raw read rejects the options that have nothing to do with it, with an explicit error: `--base`, the selection by a measure, `--with-ancestors`, `--issues` and `--human`. A document that is invalid as a node is read safely as a document and stays outside the nodes of the graph. The graph of the staged index is validated by `check`.

The public top-level commands are `init`, `query`, `add`, `update`, `delete`, `check` and `diff`. The advanced groups for sources and for spotlights each have a `show` subcommand for the reads of their own domain. Before a graph editor changes a node, it reads the saved files afresh through the read request of the application protocol, which it sends with neither a base revision nor editor text nor hints from an earlier read.

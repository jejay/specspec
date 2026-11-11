---
id: ezHjLDs=
type: requirement
parents:
- qowy5AI=
---
# Build every node path from the ID alone, in creation, in the editors and in the maintained history

The current node format requires that the name of each Markdown file directly in `.specspec` equals the full ID in its frontmatter followed by `.md`. The path is `.specspec/<id>.md` and ends in `=.md`. The validator compares the name with the ID exactly, in spelling and in letter case. A reader of the current format reports a graph of another format version and a file under another name, each with an explicit diagnostic.

`init`, `add` and the library build the path of a new node from its random full ID alone. Creation on the command line takes the text of the node, its type, its parents and, where they apply, its sources, and the creation forms of the graph editors offer the same fields. The readable label of a node comes from its text. VS Code finds node files through `**/.specspec/???????=.md` and leaves the actual validation to Python. A change of the body or of the heading leaves the path as it is. Between two revisions a node is added, modified or removed, and its path follows from its ID. An ID that begins with a hyphen is accepted as a full argument, and a new ID is checked for collisions with IDs that differ only in letter case.

This repository's own graph and the tracked Gantt example use these paths. The links in the documentation, the diagrams, the planning recipes for agents and the editor examples show node paths in this form. Every revision and tag of the maintained Gantt history, including the node files that a later revision deleted, is built by actual calls of the current command line, and its source anchors, receipts, ledger, bundle and tracked snapshot are renewed together. The checks cover the working graphs, the exact staged graphs with their sources, every commit and tag of that history and native and managed creation. A rebuild leaves local experiments and the other Git history of this repository as they are.

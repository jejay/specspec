---
id: LvYBN_4=
type: requirement
parents:
- WpYvGUo=
- PL1IogE=
---
# Keep the rules of the graph in one Python backend that the command line and both graph editors share

One reusable Python backend is the authority for the validation of the node format, the rules of the graph, the planning of Markdown edits, the transactions that write a project, the Git snapshots and the operations on source regions. The command line and both graph editors share it, and an editor reaches it through the command line, which answers in versioned JSON. An editor starts the command line as a process of its own: with the arguments as an array and without a shell, with UTF-8 standard input and output of limited size, in a working directory outside the project and with Python's safe import path. The files of a project are thus data for the backend and never code that it runs.

The installed tools carry the version of the node format and the version of the application protocol together. For a node-file editor of VS Code the backend returns an edit plan and writes nothing, and VS Code saves the document. A save in a graph panel or in the desktop app goes through the transaction writer of the backend.

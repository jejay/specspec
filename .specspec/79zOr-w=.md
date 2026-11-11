---
id: 79zOr-w=
type: requirement
parents:
- _wJJQko=
---
# Find the node files directly in .specspec and reserve .specspec/local for working data

The specification directory is `.specspec` at the project root, and it is the only one. The Markdown files directly in it are the node files, each named `<id>.md` after its full ID. The directory `.specspec/local`, of exactly this name, holds the working data of the checkout, and Git ignores it. It stands apart from the inventory of node files, which comes from the files directly in `.specspec` alone, whether the working files, the Git index or a commit is inspected. Every other entry of `.specspec` that is not a node file is reported. A symbolic link or a file in the place of `.specspec` or of `.specspec/local` is unsafe: it is reported, and the tools read and write through real directories alone.

A command finds its project by the nearest `.specspec` entry at or above the working directory and takes that entry even when it is invalid. The same layout serves the discovery in the backend, the paths of raw reads and of editor documents, the reading of the Git index and of commits, the root of source paths, the spotlights and both graph editors. This repository's own specification follows it, and so does the maintained Gantt history: every commit and tag, the nodes that a later commit deleted, the recorded receipts, the ledger and the bundle. A rebuild of that history leaves local experiments and the other Git history of this repository as they are.

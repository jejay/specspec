---
id: jsIUeP0=
type: requirement
parents:
- qowy5AI=
- v6xn2GU=
---
# Anchor a source region to a Git blob and derive its place in the working tree, the index or a revision

A source link holds a path relative to the project and an optional descriptive symbol. A link can name a whole file. A link to regions adds the full ID of an immutable Git blob, the mode strict or expanding and one or several line ranges, which are positive, inclusive and counted from 1. The position of the regions in the working tree, in the index or in a revision is derived from a textual diff of limited size, from the context of the lines and with the help of renames. A missing or deleted object, an ambiguous position and an uncertain mapping are reported.

A capture reads the committed HEAD or, on explicit request, the staged index. The anchored blob is kept by the tree of an existing commit or by the staged tree of the commit to come. A blob ID in Markdown is an address written as text, and reachability comes from Git trees. Full SHA-1 and SHA-256 object IDs are supported. Objects are read in batches, and each request has its own caches with explicit limits.

The command line inspects, captures and reanchors source links and checks them together with the graph, and both graph editors show literal previews. A capture in an editor updates the open form, and the form is saved by its usual owner, VS Code or the writer. Links to whole files and use outside a Git repository are available, and a change anywhere in a linked file counts as possible impact on every implementation that links it. A blob ID addresses immutable content, and review judges where the code came from and what it means.

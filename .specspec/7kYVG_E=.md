---
id: 7kYVG_E=
type: requirement
parents:
- 0dvOn3A=
- Yfy0414=
---
# Print a complete review diff grouped by node, with a summary first

`diff` prints a full review diff by default, with a short summary before it. The output is grouped by node and names each node by its full ID, its type, its heading and its old and new path. Every changed passage of node text appears as a hunk with context, and an added or deleted node appears in full. The diff states the exact changes of parents, type, source links and extensions. An overview lists the added and the removed links in readable form, each end labeled with its ID and with the heading it has in the revision that holds the link.

Every meaningful change of the text of a node file is shown, including a change of a frontmatter comment, of whitespace or of the final newline alone. The unified patches of node text use lines that end in LF, and two texts that differ only in the encoding of their newlines count as equal. A raw `query` gives the exact bytes of a document, and the full patches hold every other change of content. The patches are records for review, and ordinary Git supplies the patches that apply byte for byte. The summary alone is printed on the explicit request `--summary`, and the full diff is the default. An invalid or unavailable revision is reported with diagnostics that name the next step and with an impact marked incomplete, and a comparison is reported as empty only when both sides were read and are equal.

Changes of linked source files, and the nodes they may affect by the cautious count per file, are listed apart from the changes of the specification itself. The diff gives the paths of the changed files and the implementations that link them. The patches it prints are those of node files, and a node in the affected scope is reported as possibly affected, which is a scope and no verdict that it is invalid. Reading the snapshots leaves the checkout, the index, the refs and the source files as they are.

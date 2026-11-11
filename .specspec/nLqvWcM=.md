---
id: nLqvWcM=
type: requirement
parents:
- T693TDw=
---
# Draw the query tree with two-column rails and name every parent in each header

The tree indents by two columns for each level: a level with siblings still to come contributes `│` and one space, and a level whose branch is complete contributes two spaces. The branch markers `├─` and `└─` stand directly before the type word of a header or before the arrow of a reference. The header of the root has no branch marker and starts at column zero, and the metadata and the body of the root are aligned with it there. The metadata and body lines of every other node begin with the rail that continues their branch. Behind the rail the body keeps its own indentation and all its whitespace apart from newlines.

A full header gives the type as a lowercase word, `manifesto`, `requirement` or `implementation`, and the full node ID. After `@` follow all direct parents in ascending order of their full IDs, compared case-sensitively and separated by a comma and one space in every presentation. The parent under which the record is printed is among them. The header of the manifesto ends with its ID, before the comparison status where there is one. An earlier occurrence of a node with several parents is a short reference that is left unexpanded. Lowercase status words mark a change of the node, a change of linked code that matters for its link and a literal change of the node file. The lines before the tree name the selected revisions and the notes that apply, and a header explains itself.

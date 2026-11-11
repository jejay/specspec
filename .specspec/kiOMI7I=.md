---
id: kiOMI7I=
type: requirement
parents:
- 0dvOn3A=
---
# Give people and agents a compact and complete reading of a specification graph

People and coding agents read a specification graph in a form that is easy to follow and compact, so that it costs an agent few tokens. A reader takes the whole graph, or a part of it that starts at a chosen node, and can add every ancestor that is needed to understand the selected nodes. Each selected node appears once with its complete text, also a text without a heading, and with every one of its direct parents named beside it. People and agents get the same information.

Every reading compares two revisions. The reader's attention is on the current specification, and sparse hints mark what changed against the earlier revision. A node that was deleted since then keeps its complete earlier text and its place among its relationships. The detailed changes of text are found in `diff` and in the structured records of the comparison.

For a source link the reading tells three things apart: a change to the link in the node, a change to the linked code, and the place of the linked region in each of the two versions. The mode of a link says which changes of the linked code matter: a change that the mode permits stays unmarked, and a broken or uncertain link stays visible.

Reading changes nothing: the node files, the text in open editors and the Git state stay as they are. A reading comes quickly, and every call reads the saved data afresh.

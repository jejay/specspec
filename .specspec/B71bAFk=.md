---
id: B71bAFk=
type: requirement
parents:
- h3zqGZU=
---
# Show deleted nodes in the tree of a comparison, each with its former parents

The tree of a comparison is drawn from one display graph. A node that survives or was added is taken from the target revision with its current parents, and a node that exists in the base alone, a deleted node, is taken from the base with its former parents. This graph is printed as one ordinary tree. The label `deleted` marks a record that shows the complete earlier text of its node. A deleted node with several parents gets the same forward references and the same place at its last occurrence as a current node. A header names all the parents of the record that was chosen.

For valid revisions the display graph is acyclic. An invalid reference in the working files can link a current node to a parent that is missing or deleted, and input with a cycle is printed component by component in a form that is safe against cycles. The text of an earlier revision is context from history, and the reasons of a current node are its current parents. A relationship of the base that was lost between two surviving nodes is found in the structured comparison and in `diff`. The complete sets of old and of new edges are separate facts of the comparison.

Each revision is validated on its own. The display graph can contain what a single revision may not: a shortcut that the changed ancestors of current nodes have newly created, a former requirement that is typed as an implementation in the target and still has deleted children, or two manifestos from revisions that are unrelated. It is a derived reading and never a new specification. Its chosen edges and roots are shown as they are, without the checks for shortcuts, types and a single root that apply to a revision, and it is never written into node files.

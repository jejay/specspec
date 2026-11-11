---
id: apEb_pM=
type: requirement
parents:
- xu6W0c4=
- VZvwDBY=
- _yahyM4=
---
# Derive from Git snapshots which nodes are new, changed or removed

A node file holds what the node is: its ID, its type, its parent links, its text and, for an implementation, its source links. Which nodes were added, changed or removed, and which nodes a changed source file touches, is derived from the Git comparison that is selected. Why a node is new, and whether a node has to be reconsidered, is explained by the commits and their messages and judged by the owner in review.

Removing a node deletes its Markdown file. The deleted file and the explanation it gave live in the trees of the earlier commits, and the reason for the removal is in the commit message. A view of the working files compares them with HEAD as it resolves at that moment. A node that HEAD holds and the working files lack is shown as deleted, marked D, also while the deletion is staged, and it leaves the view once the deletion is committed. A comparison of chosen revisions gives access to the earlier snapshots of the specification.

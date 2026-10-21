---
id: B71bAFk=
type: requirement
parents:
- h3zqGZU=
---
# Keep deleted bindings in the selected-record comparison graph

Choose each surviving or added node from the target, including its current parents,
and each base-only deleted node from the base, including its former parents. Render
this selected-record projection in one ordinary tree-shaped reading. D marks deleted
records and their complete old bodies. Shared deleted nodes use the same forward
references and last-occurrence placement as current nodes. Headers retain all of
the chosen record's parents.

The projection is acyclic: current nodes have current parents, so no deleted node
can parent a current node; paths entering deleted nodes continue only through the
acyclic base-only subgraph. Keep lost base relationships among surviving nodes in
the structured comparison and diff. Full old/new edge unions remain separate facts.

Validate each canonical revision independently. A display projection can contain a
shortcut newly created by changed current ancestry, a former requirement now typed
as an implementation with deleted children, or two manifesto identities in unrelated
revisions. It is a derived reading, not a new canonical specification. Preserve its
chosen edges and roots without applying canonical reduction/type/root validation
or writing the projection into node files.

---
id: 2b6a0e4e-f07f-4932-b58b-40348d4c3ac1
type: requirement
parents:
- ee57a451-059d-426b-868e-e898c2503082
- 2f6ee5bd-9014-4a0c-8677-53ecbab93f92
- 2b8a4bbc-d15a-4347-90b4-691abdeefaef
- 4d1f2eee-8125-4e3f-b9b4-649517875d87
managed_hash: dfecc7e9fdf5d1c48078b789f5f41ee06cf2c149f9acb9d2f971e51b7abc8269
---
# Use an in-webview neighborhood view and explicit relationship metrics

Switch between overview and focused views in the existing local webview. Use
compact upstream and downstream groups around an expanded selected-node card, moving the
existing form into that card rather than introducing another write path. Back
returns to the overview without discarding a draft; switching to a different
node requires explicit discard confirmation if the form is dirty.

Distance means the shortest directed hop count from the manifesto, computed in
each individual snapshot, not in the potentially cyclic revision union. For a
child card, count all distinct nodes reachable below that child at any depth,
excluding the child itself. Traverse iteratively and deduplicate by ID so a DAG
with multiple paths does not inflate the total. A leaf shows zero. Label this
as downstream nodes / potential impact, not a direct-child count. Shared nodes
count once within each child's subgraph; totals for different children can overlap
and must not be presented as an additive global total.

Keep revision overlays and removed neighbors visible. Use base-snapshot context
for removed nodes, target context for surviving nodes, and mark old relationships.
No depth, count, position, or color is written into canonical node metadata.

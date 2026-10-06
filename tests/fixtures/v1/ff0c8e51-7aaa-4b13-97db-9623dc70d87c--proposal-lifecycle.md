---
id: ff0c8e51-7aaa-4b13-97db-9623dc70d87c
type: requirement
status: proposed
parents:
- c0943883-e3cb-4de9-8c5e-6aeb4a37dd06
- 003d697b-4104-4fdf-8e05-0db572c436d0
managed_hash: 92b7ffd0bc762b974c3139be8ff8790ce62d08c8c1718b74e0f67c5dc9eb1859
---
# Represent proposal selection separately from graph position

Use proposed, accepted, and retired statuses independently of relative graph
position. Accept only explicitly named nodes, with accepted parents; prevent live
nodes from depending on retired parents. Retain retired explanations in the DAG.

Existing implementation and passing tests are not approval of a proposed design.
Do not infer mutual exclusion merely because two candidates share parents.

Origin: [CONCLUSION_SPEC.md](../CONCLUSION_SPEC.md), lifecycle operations.

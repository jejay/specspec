---
id: ff0c8e51-7aaa-4b13-97db-9623dc70d87c
type: requirement
parents:
- c0943883-e3cb-4de9-8c5e-6aeb4a37dd06
- 003d697b-4104-4fdf-8e05-0db572c436d0
managed_hash: 4d9ab01d0d1af3d822e269094347290ca03952e42157aa9514435c92f8335544
retired: true
---
# Represent proposal selection separately from graph position

Use proposed, accepted, and retired statuses independently of relative graph
position. Accept only explicitly named nodes, with accepted parents; prevent live
nodes from depending on retired parents. Retain retired explanations in the DAG.

Existing implementation and passing tests are not approval of a proposed design.
Do not infer mutual exclusion merely because two candidates share parents.

Origin: [CONCLUSION_SPEC.md](../CONCLUSION_SPEC.md), lifecycle operations.

## Withdrawal

The user removed individual proposed/accepted approval gates in favor of risk-proportionate review.
History is retained; see the risk-proportionate-review intention and its separate schema conclusion.

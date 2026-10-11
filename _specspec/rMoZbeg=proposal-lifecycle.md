---
id: rMoZbeg=
type: requirement
parents:
- VZvwDBY=
- ME4UXTA=
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

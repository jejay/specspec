---
id: D9uv83Q=
type: requirement
parents:
- SvnK0jM=
---
# Respect finish-to-start prerequisites

Allow tasks to reference distinct existing prerequisites in an acyclic graph.
A successor's start follows every prerequisite's finish. Surface invalid links or
cycles before applying a candidate and retain the saved valid plan.

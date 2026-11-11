---
id: D9uv83Q=
type: requirement
parents:
- SvnK0jM=
---
# Respect finish-to-start prerequisites

A task names other existing tasks as prerequisites, without cycles, and starts after all
of them have finished. A link to a missing task or a cycle is reported before the change
is applied, and the saved valid plan stays.

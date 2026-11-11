---
id: ZagrM6Q=
type: requirement
parents:
- evfMtUM=
---
# Bound every test run in time

A unit test that never finishes fails as timed out within two minutes. Each CI job
has a time limit of a few times its usual duration, so a process that blocks or stays
alive ends within minutes with the job marked failed. The platform's own limit is six
hours.

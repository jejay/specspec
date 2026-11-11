---
id: kvBgyYw=
type: requirement
parents:
- r1wddEQ=
- 3wsnEjk=
---
# Keep graph and product in sync while building, and report contradictions

While it builds, the agent keeps the specification and the product in sync: it records what the graph leaves to it as conclusions, explains what it built in implementation nodes and keeps existing explanations and source links current. Removing nodes is for the owner to decide. When nodes contradict each other, the agent builds a simple, broad part of the graph that is free of the contradiction and reports the conflict, the part it chose and what follows from it. An idea for improving the product is reported as well, and either can be worked out as a graph on a separate branch. Passing tests are evidence for the owner's review, and every conclusion stays open to replacement.

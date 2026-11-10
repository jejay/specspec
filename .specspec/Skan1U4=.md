---
id: Skan1U4=
type: requirement
parents:
- evfMtUM=
---
# Run the checks that cover a change

Before reporting work as done, an agent runs the checks whose inputs it changed. The
complete Python suite takes about ten minutes locally and runs when Python code
changed. Graph nodes, documents and the agent guide have the two graph checks and
their own test files, which finish in seconds. The UI suites run for UI code, and the
history verifier for the Gantt example. CI runs the complete list on every push and
pull request.

---
id: EIDAkpU=
type: requirement
parents:
- zBmAdi4=
---
# Run the commands a model writes with specspec's own command line

A quiz on the commands asks for the command lines of a change to a given graph. The quiz
splits each line into words the way a shell does, runs it on a temporary copy of that
graph and judges the graph that the commands leave behind. Only `add`, `update` and
`delete` run. The verdict comes from specspec itself, without a grader.

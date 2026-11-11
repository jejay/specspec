---
id: 0piRXe0=
type: requirement
parents:
- -RQn7Ug=
---
# Apply add, update and delete steps to an invalid graph and require a valid result only on request

`add`, `update` and `delete` work on targets that are safe to write and identified uniquely, also when the graph around them is invalid and when their result is invalid. They diagnose the complete result and print a receipt that says that the edit was applied, whether the graph is valid and whether the analysis is complete. An edit that is applied counts as a success also when the graph is invalid. With `--require-valid` an edit whose whole result would be invalid is rejected before anything is written. `check` stays strict, also on staged content with its sources, and judges each source mapping that is usable on its own.

One invocation can combine a limited number of explicit `add`, `update` and `delete` steps, with literal `-m` messages, with bodies that an integration supplies as input and with local aliases for the IDs of nodes that the invocation creates. The whole grammar of the steps is parsed before any input is read and before anything is written. A command that is no editing step is rejected among them, and so are edits that are ambiguous or in conflict. The complete candidate is saved in one transaction that can be recovered, `--dry-run` writes nothing, and a final validity check is optional. An alias exists for its invocation alone: the node files store the generated IDs and nothing of the alias, and an ID is taken when the invocation writes its node. In a chain a deletion needs the same consent and passes the same byte checks of the transaction as on its own.

The application protocol carries this behavior to the command line and to the graph editors, and the exit codes follow the application protocol. A read that is explicitly incomplete returns what it could read, with a nonzero status. A saved edit is reported as saved whatever diagnostics come with it.

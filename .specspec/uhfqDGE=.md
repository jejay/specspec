---
id: uhfqDGE=
type: implementation
parents:
- 6SyZ-BU=
sources:
- path: src/specspec/workspace.py
- path: tests/test_additional.py
- path: tests/test_core.py
- path: tests/test_ids.py
- path: tests/test_markdown.py
---
# Apply edits as journaled, byte-checked transactions and recover interrupted ones

`src/specspec/workspace.py` holds the writer. `mutate` takes the lock, loads the saved files and requires the current format, builds the candidate from the changes of an edit and validates it, records the original and the new bytes of every changed path in the journal, compares each target with its original bytes and replaces it. Validation means that every document to be written parses as a node of the current format and, on request, that the complete graph is valid. A change whose new state is null deletes the file. `add_node` generates an ID inside the lock and generates another while the ID collides with one that is taken. `update_node` keeps the ID and changes the fields that are named. `delete_nodes` carries out the plan for exactly the selected files and, when a reviewed plan is given, only if the plan it computes under the lock equals it. `initialize` validates the graph of the given manifesto text, stages it and publishes it. It also creates the packaged guide as `AGENTS.md` at the project root, or appends the guide after an `AGENTS.md` that is already there.

`recover` restores a file only from a state that the journal knows, the original bytes, the new bytes or absence, and it keeps text that somebody else wrote in the meantime for the user to resolve. A writer that has acquired the lock checks once more for a journal or staged files before it proceeds. `tests/test_additional.py`, `tests/test_core.py`, `tests/test_ids.py` and `tests/test_markdown.py` exercise unsafe state, the deletion of node files, the recovery of an initialization and of leftover staging, and ID collisions under the lock. Competing writers, byte races and interruptions are exercised in `tests/test_transactions.py` and `tests/test_recovery.py`. The writer protects cooperating writers and survives an interrupted process. It stays within what the file system gives: staging and node files lie on one file system, and a race with a program outside the lock and durability after a loss of power are as the file system has them.

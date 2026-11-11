---
id: kdTk6-0=
type: implementation
parents:
- 4626uI8=
sources:
- path: src/specspec/cli.py
- path: src/specspec/edit_cli.py
- path: src/specspec/batch.py
- path: src/specspec/output.py
- path: tests/test_cli_chains.py
- path: tests/test_cli_arguments.py
- path: tests/test_cli_compact.py
- path: tests/test_invalid_workflow.py
- path: example/gantt/history/cli.jsonl
- path: example/gantt/history/gantt.bundle
- path: example/gantt/history/revisions.json
---
# Split a chain into steps before any write and plan it as one candidate for the writer

`src/specspec/edit_cli.py` finds the boundaries of the steps from the number of values that Click declares for each option. It counts the two values of a replacement, also when OLD is attached to the option, keeps every option value literal and parses all steps before a command callback runs. `src/specspec/cli.py` rejects a step with conflicting sources for its body and prepares explicit add, update and delete records. The bytes of all text that an invocation supplies are charged to one budget as each input is loaded, and nothing further is read once the budget is exceeded. The flags of the invocation decide once for all steps between preview and write, whether the final graph must be valid, the consent to deletions and the form of the output. An ordinary single `add`, `update` or `delete` calls the writer directly, with the envelope of a single edit and, for `delete`, with its reviewed deletion plan. An `add` with a local name, a preview of `add` or `update` and an `update` with exact body replacements use the batch planner.

The batch planner in `src/specspec/batch.py` allocates safe IDs under the lock, resolves a local name as a parent whether its step stands before or after, rejects conflicting edits of one target and builds one candidate for the journaled writer. A local name stays out of the node files. `src/specspec/output.py` reports the actual IDs behind the local names in the readable receipt, and the JSON receipt carries them too. The graph editors send single edits with the body on standard input, use the application protocol and save through VS Code or the writer.

`tests/test_cli_chains.py`, `tests/test_cli_arguments.py`, `tests/test_cli_compact.py` and `tests/test_invalid_workflow.py` cover chains with deletion, replacement and several parents, the exact association of bodies and sources with their steps, the checks of syntax and input before any write, command and option words as literal values, local names, the flags of the invocation, consent to selected deletions and its cancellation, the behaviour of a single step, the limits, source inputs and the recovery of an interrupted chain of mixed steps. Tests with a real subprocess pass Unicode and CRLF in arguments under legacy output encodings. The independent, maintained revisions of the Gantt example, their actual receipts in `example/gantt/history/cli.jsonl`, their sources, the bundle and the ledger `example/gantt/history/revisions.json` are consistent with this command line.

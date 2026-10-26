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
- path: docs/cli.md
- path: docs/invalid-graphs.md
- path: docs/investigations/editing-chains.md
- path: example/gantt/history/cli.jsonl
- path: example/gantt/history/gantt.bundle
- path: example/gantt/history/revisions.json
---
# Implement composed edits through complete CLI preflight and the shared writer

edit_cli.py identifies step boundaries with the declared Click option arities,
including two-value replacement options and attached OLD values,
retains literal option values and parses every step before callbacks. cli.py
preflights body-source conflicts and prepares explicit add/update/delete records.
Aggregate authoring bytes are charged as inputs load, stopping before further reads
once the budget is exceeded.
Invocation-wide flags select one preview/write, final validity boundary, consent
and output mode. Ordinary singleton calls keep their current writer, envelope and
reviewed-deletion behavior; named adds, add/update previews and exact body
replacements use the batch planner.

The internal batch planner allocates safe IDs under lock, resolves forward/backward
parent aliases, rejects conflicting targets and constructs one candidate for the
existing journaled writer. Local aliases remain outside canonical data. Output
reports actual alias mappings in readable and JSON receipts. Host products retain
their single-edit stdin and API-7 channels and native/managed persistence owners.

Tests cover composed deletion/replacement/coparents, exact body/source association,
syntax/input preflight, literal command/option words, aliases, invocation-wide flags,
selected consent/cancellation, singleton compatibility, bounds, source inputs and
mixed-operation interruption/recovery. Real subprocess tests preserve Unicode/CRLF
arguments under legacy output encodings. Independent maintained Gantt revisions,
actual receipts, sources, bundle and ledgers retain current-interface consistency.
Verification and platform boundaries are recorded with the source-linked guide.

---
id: Fy-_P9A=
type: implementation
parents:
- BKekD_o=
sources:
- path: docs/cli.md
- path: docs/invalid-graphs.md
- path: example/gantt/history/cli.jsonl
- path: example/gantt/history/gantt.bundle
- path: example/gantt/history/revisions.json
- path: example/gantt/history/verify.py
- path: src/specspec/batch.py
- path: src/specspec/cli.py
- path: tests/test_api.py
- path: tests/test_cli_arguments.py
- path: tests/test_cli_compact.py
- path: tests/test_invalid_workflow.py
- path: docs/investigations/argument-authoring.md
---
# Implement direct argument authoring with an unchanged host seam

cli.py shares literal message parsing across init/add/update and bounds encoded body
bytes before joining paragraphs. The argument source is distinct from hidden bulk
body input; missing/conflicting sources fail before filesystem mutation. apply
parses inline JSON with duplicate-key rejection and passes an explicit body-file
policy to batch.prepare. The domain writer, alias allocation, deletion consent,
optional validity boundary and API-7 envelopes retain their existing owners.

The UI session, one-shot bridge and persistent API channels retain their current
argv/stdin contracts. Tests cover literal filenames/dashes/Markdown/control text,
Unicode/CRLF and exact whitespace, repeat/omit/empty/conflicting messages, byte
bounds, primary help, inline forward aliases/dry-run/rejection, relative bulk files,
large stdin and real shell-free Unicode argv under legacy output encodings.

Maintained example verification independently reconstructs bodies from literal
message arguments. Every retained Gantt revision/ref is rebuilt through actual
current CLI executions with refreshed receipts, source anchors, ledger and bundle.
Historical identities, app bytes, redirects and existing manual clones retain
their established roles. Native document persistence and managed writes remain
separate. Guides distinguish OS argument limits from the unchanged bulk limits.

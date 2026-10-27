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
# Implement message and automatic-stdin authoring through the shared writer

The CLI shares bounded literal paragraph joining and automatic UTF-8 stdin input
across init/add/update. It rejects obsolete body options. Body-mode selection happens
after complete grammar/field preflight; replacements do not read stdin, empty metadata
updates retain their body, and a nonempty stream cannot target multiple steps.

The common UI session omits body options and sends complete managed body text on
stdin. Native document planning/save ownership remains separate. Tests cover direct
and redirected bodies, messages without reads, empty/invalid/oversized input,
metadata preservation, replacement isolation, chain ambiguity and actual subprocess
transport. Serialization retains document style, meaningful whitespace and EOF rules.
Maintained receipts are real current CLI executions across the complete Gantt history.

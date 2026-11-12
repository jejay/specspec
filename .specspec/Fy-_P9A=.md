---
id: Fy-_P9A=
type: implementation
parents:
- BKekD_o=
sources:
- path: example/gantt/history/cli.jsonl
- path: example/gantt/history/gantt.bundle
- path: example/gantt/history/revisions.json
- path: example/gantt/history/verify.py
- path: src/specspec/batch.py
- path: src/specspec/cli.py
- path: tests/test_api.py
- path: tests/test_cli_arguments.py
- path: tests/test_cli_compact.py
- path: tests/test_first_use_messages.py
- path: tests/test_invalid_workflow.py
---
# Implement message and automatic-stdin authoring through the shared writer

The CLI shares bounded literal paragraph joining and automatic UTF-8 stdin input
across init/add/update. Body-mode selection happens
after complete grammar/field preflight; replacements do not read stdin, empty metadata updates retain their body, and a nonempty stream cannot target multiple steps. Standard input that is a terminal, including the NUL device that Windows reports as one, is never read: metadata-only steps keep their bodies and other steps stop with the NO_TEXT hint naming -m and piped text, as empty init/add input does. read_body drops a leading byte-order mark and names the first byte that is not UTF-8.

The common UI session omits body options and sends complete managed body text on
stdin. Native document planning/save ownership is separate. Tests cover direct
and redirected bodies, messages without reads, empty/invalid/oversized input,
metadata preservation, replacement isolation, chain ambiguity and actual subprocess
transport. Serialization retains document style, meaningful whitespace and EOF rules.
Maintained receipts are real current CLI executions across the complete Gantt history.

---
id: i7aT1lc=
type: implementation
parents:
- qowy5AI=
- evfMtUM=
sources:
- path: src/specspec/model.py
  symbol: ID_RE
- path: src/specspec/format.py
  symbol: parse_node, serialize
- path: src/specspec/workspace.py
  symbol: new_node, initialize, add_node, snapshot_from_files
- path: src/specspec/cli.py
  symbol: ID argument commands and export_graph
- path: src/specspec/editor.py
  symbol: editor_request
- path: tests/test_ids.py
- path: tests/test_core.py
- path: tests/test_recovery.py
- path: graph-ui-common/media/graph.js
  symbol: full ID cards and parent controls
- path: graph-ui-common/host/session.cjs
  symbol: current-schema mutations
- path: graph-ui-common/view.cjs
  symbol: no schema migration controls
- path: graph-ui-common/test/graph.test.cjs
  symbol: compact full-ID messages and renderer regressions
- path: vscode/package.json
  symbol: customEditors filenamePattern
- path: vscode/src/host.js
  symbol: current project-scoped state
- path: vscode/src/extension.ts
  symbol: current document/managed mutation dispatch
- path: electron/security.cjs
  symbol: current allowed actions
---
# Generate canonical compact IDs and reject superseded node schemes

The model validates exactly seven Base64url symbols and one equals sign, with
zero final pad bits. The workspace uses secrets.token_bytes(5), retaining all
40 random input bits. New-node creation runs inside the managed writer lock and
retries against every live/withdrawn ID, including case-only aliases independently
of summary. Input graphs reject portable case-only duplicates. IDs, parents and
paths use the full trailing equals sign; no double-hyphen separator remains.

Current format/API 3 retains the hash-free typed metadata and rooted DAG, but
removes obsolete version readers/hash-status normalization, migrate CLI/library
code and host controls. Old files/unsupported snapshots yield diagnostics, not
silent repair. Recovery, original-byte checks, journals/locks, manual editing,
withdrawal and host authorization remain. A one-time ignored temporary migration
validated the two captured working graphs, saved mappings/original bytes and
journaled replacement/deletion of their canonical files; it is not shipped code.
Both root and example nodes, parent lists and relevant current documentation links
were converted. Superseded compatibility evidence is explicitly scoped as history.

Mermaid hex-encodes full ASCII IDs injectively. CLI ID commands accept hyphen-leading
Base64url IDs without interpreting unknown short/long option-looking IDs as flags;
normal declared options still parse, and explicit -- is also usable. The shared
renderer displays full IDs without truncation. VS Code associates exactly seven
payload characters plus equals/summary with the custom editor. The pre-extraction
unscoped draft-state compatibility fallback is removed; current per-project node
records/drafts remain. Persisted pre-rekey drafts/cameras are not rekeyed or claimed
compatible; users should copy needed old drafts.

Local verification: all 100 Python tests, Ruff lint/format and both warnings-as-errors
working validators passed. Tests exercise fixed byte vectors, every possible final
octet, malformed padding/alphabet/length, full CLI/editor/Mermaid IDs, hyphen-leading
IDs, lock-scoped live/withdrawn/casefold collision retries, portable duplicates,
old-schema rejection, strict metadata, comments/body/extension preservation and
interrupted ordinary edits/recovery. Shared UI, VS Code adapter and Electron unit
commands passed; the final suites have 99 shared, 34 VS Code and nine desktop
unit tests, including the added full-ID renderer regression.
Real Windows host verification is scoped by the separate fixture conclusion and
history implementation record, not proof of universal graph behavior.

---
id: huB7hcg=
type: implementation
parents:
- AuhoBoU=
sources:
- path: src/specspec/deletion.py
- path: src/specspec/workspace.py
- path: src/specspec/cli.py
- path: src/specspec/git.py
- path: graph-ui-common/host/session.cjs
- path: graph-ui-common/host/documents.cjs
- path: graph-ui-common/media/graph.js
- path: graph-ui-common/view.cjs
- path: graph-ui-common/test-host/budgets.cjs
- path: tests/test_cascade_deletion.py
- path: tests/test_deletion.py
- path: tests/test_core.py
- path: tests/test_transactions.py
- path: tests/test_ids.py
- path: graph-ui-common/test/session.test.cjs
- path: graph-ui-common/test/graph.test.cjs
- path: vscode/test/extension.test.cjs
- path: vscode/test/budgets.test.cjs
- path: graph-ui-common/test-host/platform.cjs
- path: vscode/test-host/run.cjs
- path: vscode/test-host/smoke.cjs
- path: vscode/test-host/documents.cjs
- path: electron/test-host/run.cjs
- path: example/gantt/history/verify.py
- path: example/gantt/history/gantt.bundle
- path: docs/deletion.md
- path: docs/native-editors.md
- path: docs/architecture.md
- path: docs/architecture.svg
- path: docs/own-spec.md
- path: graph-ui-common/test/host-ui.test.cjs
---
# Execute reviewed exact-file deletion and report retained dependency faults

The shared deletion planner selects only requested identifiable IDs, assesses selected
paths with ordinary Git semantics, and computes surviving broken references and
potential descendants without selecting them for removal. CLI and hosts share the
preview, warning, consent and under-lock reviewed-plan checks. The journaled writer
removes only selected files and reports the resulting graph independently of applied
operation success. Recovery restores recognized bytes, including invalid originals.

Regression coverage includes shared/exclusive/deep descendants, overlapping explicit
selections, unchanged survivor bytes/parents, staged/new/ignored/comment/mode/rename/
unmerged warnings, cancellation, changed plans, byte races and recovery. Historical
D context remains distinct from current missing endpoints through stage/commit.
Native dirty resources and linked code are protected. Shared host probes use the
independent maintained current-schema Gantt history and exact fixture indexes.

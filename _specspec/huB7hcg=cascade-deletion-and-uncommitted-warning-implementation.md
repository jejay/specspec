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
# Execute a reviewed descendant cascade with pre-write warnings

`deletion_plan` traverses saved directed children iteratively and deduplicates all
requested/full/shared/deeper descendants. It assesses every canonical path with
bounded NUL-delimited Git status and emits explicit uncommitted/unavailable warnings.
CLI `delete --dry-run` returns the plan; consent retains warnings before unlinking.
`delete_nodes` replans inside `mutate` and compares reviewed scope/paths/status records.
Changed plans fail before canonical writes. Successful output names the entire closure.

The writer validates the surviving DAG, byte-checks originals and journals each
null replacement for recovery. Outside parents and linked source files remain
unchanged. Shared hosts preview the same backend, confirm scope/warnings and supply
bounded reviewed-plan stdin. ProjectDocuments protects dirty native resources.

Regression cases cover sole/shared/deeper/overlapping roots, staged/new/ignored/
comment/renamed/unmerged nodes, cancellation/noninteractive consent, changed plans,
byte races and recovery. Maintained-history real-host checks cover all cascade D
records through staging until commit and empty base membership for uncommitted nodes.

The real-host cascade fixture selects live manifesto siblings present in its HEAD,
excluding uncommitted setup additions. Its Git wrapper validates the exact staged
graph before every fixture commit. Deterministic helper coverage places an
uncommitted root child first and checks that a retained outside parent is chosen.

The Electron reload/revision probe polls for the asynchronously requested comparison
dialog's actual open state within its existing reload readiness allowance before
applying stage refs. Its substantive revision and workspace assertions remain intact.

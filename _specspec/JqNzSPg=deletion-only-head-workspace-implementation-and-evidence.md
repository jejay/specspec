---
id: JqNzSPg=
type: implementation
parents:
- 5d5oDCM=
sources:
- path: src/specspec/model.py
  symbol: SpecNode, FORMAT_VERSION, API_VERSION
- path: src/specspec/format.py
  symbol: FIELDS, parse_node, serialize
- path: src/specspec/graph.py
  symbol: build_graph
- path: src/specspec/workspace.py
  symbol: delete_nodes, mutate, recover
- path: src/specspec/cli.py
  symbol: delete, list_nodes, context, hook_check
- path: src/specspec/editor.py
  symbol: editor_request missing-buffer reads and absent-field plans
- path: src/specspec/git.py
  symbol: unborn_head, git_snapshot, semantic_diff
- path: src/specspec/source_commands.py
  symbol: current implementation source operations
- path: graph-ui-common/host/git-watch.cjs
  symbol: GitWatcher
- path: graph-ui-common/host/session.cjs
  symbol: GraphSession.handle, refresh, readGraph
- path: graph-ui-common/host/documents.cjs
  symbol: ProjectDocuments.mutate, readGraph
- path: graph-ui-common/media/graph.js
  symbol: updateButtons, loadForm, select, snapshot focus reconciliation
- path: graph-ui-common/media/graph-model.js
  symbol: displayGraph, sameNode, per-snapshot metrics
- path: graph-ui-common/view.cjs
  symbol: Delete control, HEAD workspace label
- path: vscode/src/extension.ts
  symbol: GraphProject GitWatcher, GraphView bound Delete
- path: vscode/src/bridge.ts
  symbol: API-5 node type
- path: electron/main.cjs
  symbol: loadProject shared GitWatcher lifecycle
- path: electron/security.cjs
  symbol: deletion message allowlist
- path: tests/test_deletion.py
- path: tests/test_core.py
- path: tests/test_ids.py
- path: tests/test_editor.py
- path: tests/test_transactions.py
- path: tests/test_gantt_example.py
- path: tests/test_gantt_git.py
- path: graph-ui-common/test/git-watch.test.cjs
- path: graph-ui-common/test/graph.test.cjs
- path: graph-ui-common/test/documents.test.cjs
- path: graph-ui-common/test/session.test.cjs
- path: vscode/test/extension.test.cjs
- path: graph-ui-common/test-host/fixture.cjs
- path: graph-ui-common/test-host/platform.cjs
- path: graph-ui-common/test-host/ui.cjs
- path: example/gantt/history/verify.py
- path: example/gantt/history/gantt.bundle
- path: example/gantt/history/revisions.json
- path: example/gantt/history/cli.jsonl
- path: docs/deletion.md
- path: docs/native-editors.md
- path: docs/own-spec.md
- path: docs/architecture.md
- path: docs/architecture.svg
---
# Implement deletion-only nodes and a freshly HEAD-relative workspace graph

Implement xu6W0c4= through 5d5oDCM=. The user's new intention, separate detailed
mechanism and amended apEb_pM= conclusion remain separately addressable. This
supersedes retirement rather than adding another state. Current-only format/API
5 removes retired from canonical fields, dataclasses, serialization, semantic
records, editor plans and JSON; removes retire/restore commands, list filters,
include-retired, host messages, controls and badges. Invalid older schemas/fields
are rejected, not normalized. IDs, source-blob regions, colors, shapes, camera and
renderer-only label persistence remain unchanged.

workspace.delete_nodes deletes explicitly named files, protects the manifesto,
validates the remaining DAG before any deletion and never cascades or reparents.
mutate now supports null replacements alongside bytes in one original-byte checked,
locked/journaled operation; recover recognizes absent replacement state and refuses
new external text. Physical deletion is not a filesystem-atomic or adversarial race
promise. CLI normal delete returns the present graph/changed IDs and never stages,
commits, writes reasons elsewhere or installs hooks. Users explain why in Git.
Current source checks have no retired special cases; earlier deleted hints stay
accessible through current-schema Git comparisons.

Shared GraphSession defaults/resets to HEAD and rereads its current value; display
union preserves D/base text/edges until commit, including staged deletions. Body
and source fields are read-only/selectable for ghosts and historical nodes; managed
Delete/Save/Capture cannot recreate a ghost. After commit removes the last base
membership, clean focus returns to overview. Dirty out-of-band forms remain copyable
and unsavable. Native forms/caret/cameras and per-view comparisons remain separate.
Native Delete drains received edits, checks the bound ID, confirms and uses the
managed project mutation, which refuses any dirty SpecSpec document; it is not a
retired-field edit waiting for Save. Overlay reads ignore missing-file buffers
while still checking input/path/size; edits to missing files fail. Native Save is
still VS Code persistence, not a Python-managed transaction or deletion undo.

New shared GitWatcher observes private Git HEAD/index and shared packed refs/current
symbolic-ref directory ancestry, including unborn repositories, branch creation,
detached HEAD and linked worktrees. Directory notifications survive ordinary atomic
ref replacement; discovery/paths are bounded. Non-Git remains supported, and
repository creation at the project root is observed. Both hosts use the same watcher,
with VS Code Git events retained as supplemental hints. No recursive watch, default
polling, object/ref/index write or all-filesystem delivery guarantee. Optional
polling/Refresh and explicit unavailable-comparison notes remain. A genuinely unborn
symbolic HEAD has an empty baseline; arbitrary bad refs and non-Git are not passed
off as successful comparisons. Old root schemas remain deliberately unsupported.

The root was converted once through saved original bytes, staged replacements,
lock/journal/byte checks, validation and recovery-compatible records. Removed six
already-retired files: EKAJyVM= (obsolete v1 schema), lnjP2Qk= (withdrawn managed
integrity), MMGLSSY= (replaced sidebar host), rMoZbeg= (rejected approval lifecycle),
uZYoQ_w= (rejected approval-receipt gate), yWTbmx4= (replaced TypeScript CLI candidate).
Their original text remains in earlier Git commits, not copied retired nodes. This
commit's message records why. Other intentions/IDs are preserved; current conclusions
and affected implementation references label older results/workflows as history.
A first parent-amend attempt correctly rejected a cycle through the old backend/Git
conclusions; linking the amended choice to the new intention avoids manufacturing
agreement or changing rooted-DAG validation. No permanent converter/old reader shipped.

Reconstructed Gantt's ENTIRE maintained corpus from actual current CLI executions,
not merely HEAD: eight commits/tags, 123 API-5 receipts, 44 node identities across
history, two deletion batches of 13/17 and 9/16, and a 22-node final graph. Redirect
commit messages explain the product/date-model reasons. Earlier nodes/text/parents/
sources remain in their preceding commits, no flagged HEAD files. Rebuilt full
bundle, ledger, consistent IDs, staged blob anchors, every spec/code pair and snapshot;
all revisions/source retention/index/receipts/context/impact and three historical
model stages verify with current tools. Prior bundles/attempts and root saved bytes
remain local diagnostics. Development Git history is not rewritten. Existing
manual clones/experiments were preserved; new independent manual comparison clone:
C:/Users/julia/Projects/specspec-examples/gantt-deletion.

Actual checks: 157 Python, 139 shared UI, 35 VS Code adapter and nine Electron tests,
Ruff lint/format, both working graphs, full Gantt history verifier. Twenty final app
model cases and installed Chromium browser checks passed in the new independent
clone; offline palette-playground browser passed. Both complete Windows real-host
suites passed on fresh builds. Their real Git test removes a terminal file, checks
read-only/selectable D details, stages only that deletion (D remains), commits its
reason and waits for D to disappear via Git watching with NO Refresh/default polling.
They retain all palette/radii/camera/native-form/shape/ink assertions and historical
comparison/watcher/invalid-file/draft/native-document tests. Real geometry continues
the earlier documented reduced-motion/unthrottled isolated profile; no production
camera/geometry assertion or operation deadline was changed for this task.

Retain failed evidence: first focused Python run 102/103 passed; missing-buffer
skipping had bypassed an invalid-value check, fixed by validating values before
skipping. First common run 137/139 passed: old historical-disabled assertion changed
to read-only/copyable/no-save checks, and changed-title fixture expectation corrected.
First VS Code adapter run 33/34 passed; its old requires-API-4 diagnostic expectation
was updated to API 5. First full lint found long lines/imports and later Gantt test
formatting; formatting/import fixes passed without semantic weakening. Both first
real-host runs passed. These are actual dispatched bounded checks, not every OS/theme,
remote CI, universally safe deletion, guaranteed event delivery or semantic proof.

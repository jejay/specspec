---
id: JqNzSPg=
type: implementation
parents:
- 5d5oDCM=
sources:
- path: src/specspec/model.py
- path: src/specspec/format.py
- path: src/specspec/graph.py
- path: src/specspec/workspace.py
- path: src/specspec/cli.py
- path: src/specspec/editor.py
- path: src/specspec/git.py
- path: src/specspec/source_commands.py
- path: graph-ui-common/host/git-watch.cjs
- path: graph-ui-common/host/session.cjs
- path: graph-ui-common/host/documents.cjs
- path: graph-ui-common/media/graph.js
- path: graph-ui-common/media/graph-model.js
- path: graph-ui-common/view.cjs
- path: vscode/src/extension.ts
- path: vscode/src/bridge.ts
- path: electron/main.cjs
- path: electron/security.cjs
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
# Display HEAD ghosts and reconcile Git notifications in both hosts

`GraphSession` defaults/resets to HEAD and rereads its current base; `displayGraph`
retains removed base records/edges/text through staging. Ghost/history details
are selectable read-only and working actions follow target membership. Clean focus
returns to overview when commit removes its base record; dirty orphan forms remain
copyable/unsavable. Metrics and per-view comparisons stay revision-local.

Shared `GitWatcher` observes private HEAD/index and shared packed/symbolic-ref
directory ancestry, handling ordinary atomic replacements, new/unborn/detached refs
and linked worktrees with bounded discovery. Both adapters share its lifecycle and
keep optional polling/Refresh explicit. Git tests and real-host fixtures delete,
stage and commit files while checking actual ghost lifetime through notifications.
Native missing-buffer/dirty-document guards preserve existing input.

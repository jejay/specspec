---
id: 9KcV8EM=
type: implementation
parents:
- tvic3PQ=
- 6SyZ-BU=
- LvYBN_4=
sources:
- path: src/specspec/model.py
- path: src/specspec/format.py
- path: src/specspec/workspace.py
- path: src/specspec/cli.py
- path: src/specspec/git.py
- path: graph-ui-common/host/session.cjs
- path: graph-ui-common/host/watch.cjs
- path: graph-ui-common/media/graph-model.js
- path: graph-ui-common/media/graph.js
- path: vscode/src/extension.ts
- path: vscode/package.json
- path: electron/main.cjs
- path: tests/test_markdown.py
- path: tests/test_ids.py
- path: graph-ui-common/test/session.test.cjs
- path: graph-ui-common/test/watch.test.cjs
- path: graph-ui-common/test/graph.test.cjs
- path: vscode/test/extension.test.cjs
- path: graph-ui-common/test-host/platform.cjs
- path: example/gantt/history/verify.py
- path: .github/workflows/ci.yml
- path: graph-ui-common/view.cjs
- path: graph-ui-common/media/graph.css
- path: graph-ui-common/test/graph-model.test.cjs
- path: graph-ui-common/test-host/ui.cjs
- path: vscode/test-host/run.cjs
- path: vscode/test-host/smoke.cjs
---
# Reconcile watcher updates with native forms and original records

`GraphSession` serializes/coalesces refresh hints, retries transient reads twice,
compares records and controls explicit default-off polling. Shared file/Git watchers
track relevant directories/refs and reattach after ordinary replacement/recreation.
Host configuration and disposal manage their lifecycle.

Renderer drafts retain original records with native DOM/caret/camera. Same-node
changes require overwrite confirmation; unrelated changes preserve save eligibility.
Invalid reads retain a marked last valid view and diagnostics. Missing-node forms
remain copyable/unsavable. Sequence/full-membership acknowledgements check visible
render completion. Unit and host fixtures exercise external saves, incomplete/invalid
files, watcher errors, disposal, overlays and retained user input.

Initial VS Code working context is visibly provisional while comparison loads.
Shared in-flight reads and verified derived hints preserve current-read and
mutation guards; complete comparisons retain sequence/membership acknowledgements.

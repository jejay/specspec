---
id: 9KcV8EM=
type: implementation
parents:
- 6SyZ-BU=
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
# Refresh both graph editors on file and Git notifications and keep unsaved forms

`GraphSession` in `graph-ui-common/host/session.cjs` takes a notification as a hint to refresh. It runs its operations one after another, merges hints that arrive close together into one refresh, retries a transient failure of a read twice and compares the loaded records with the ones it shows, so that an unchanged graph is left as drawn. It controls the polling, which is explicit and off by default. The desktop app watches the node files with `GraphWatcher` in `graph-ui-common/host/watch.cjs`, which follows the project directory and `.specspec` and attaches again after `.specspec` was replaced or created anew. VS Code watches them with its own file-system watcher in `vscode/src/extension.ts`. Both editors share a watcher for Git, which follows HEAD and the refs and attaches again after a directory of refs was replaced. `vscode/src/extension.ts`, with the polling setting in `vscode/package.json`, and `electron/main.cjs` configure the watchers and the polling and dispose of them.

A draft in the renderer, `graph-ui-common/media/graph.js`, keeps the record it was loaded from, and a refresh leaves its form elements, its text cursor and its camera in place. Saving a draft whose node changed outside requires a confirmation to overwrite, and a change to other nodes leaves the draft ready to save. A read of a graph that breaks a rule publishes the relationships as they are, with their diagnostics. A load that is unavailable keeps the last usable graph on screen, marked as such. The data of a form whose document does not parse as a node is kept apart from the nodes of the graph, so that an empty body and half-typed source JSON can still be repaired. The form of a node that is missing can be copied from and cannot be saved. The session takes a rendering as complete when the renderer acknowledges its sequence number and the full set of visible nodes. `graph-ui-common/test/session.test.cjs`, `graph-ui-common/test/watch.test.cjs`, `graph-ui-common/test/graph.test.cjs`, `vscode/test/extension.test.cjs` and the host fixtures under `graph-ui-common/test-host` and `vscode/test-host` exercise saves from outside, incomplete and invalid files, watcher errors, disposal, editor text laid over the files and input that the user has typed.

In both editors the first graph of a view comes from the working files alone and is shown as provisional while the comparison loads. Identical reads that are under way are shared, and hints derived from an earlier read are used once they are verified. Two guards hold alongside: a read whose documents or project generation changed while it ran is discarded, and every change is preceded by a fresh read of the saved files. A complete comparison is acknowledged by sequence number and visible nodes like every other rendering.

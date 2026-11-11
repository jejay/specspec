---
id: _ANZHCw=
type: implementation
parents:
- GQdmCrA=
sources:
- path: src/specspec/editor.py
- path: src/specspec/cli.py
- path: graph-ui-common/host/documents.cjs
- path: graph-ui-common/host/session.cjs
- path: graph-ui-common/media/graph.js
- path: graph-ui-common/test/documents.test.cjs
- path: graph-ui-common/test/session.test.cjs
- path: graph-ui-common/test/graph.test.cjs
- path: graph-ui-common/test-host/ui.cjs
- path: vscode/package.json
- path: vscode/src/extension.ts
- path: vscode/test/extension.test.cjs
- path: vscode/test-host/documents.cjs
- path: vscode/test-host/smoke.cjs
- path: vscode/test-host/run.cjs
- path: tests/test_editor.py
- path: electron/main.cjs
- path: branding/activity-icon.svg
- path: graph-ui-common/media/graph-camera.js
- path: graph-ui-common/media/graph-model.js
- path: graph-ui-common/media/graph.css
- path: graph-ui-common/src/graph-vendor.js
- path: graph-ui-common/test-host/platform.cjs
- path: graph-ui-common/test/graph-model.test.cjs
- path: graph-ui-common/view.cjs
- path: tests/test_ids.py
- path: vscode/.vscodeignore
- path: vscode/LICENSE
- path: package-lock.json
- path: vscode/scripts/build-webview.cjs
- path: vscode/src/bridge.ts
- path: vscode/src/host.js
- path: vscode/src/project.ts
- path: vscode/src/view.ts
- path: vscode/test-host/ui.cjs
- path: vscode/test/bridge.test.cjs
- path: vscode/test/host.test.cjs
- path: vscode/test/project.test.cjs
---
# Connect the node-file editors and graph panels of VS Code to the shared session

In `vscode/src/extension.ts`, `GraphEditors` is the custom editor provider for the pattern `**/.specspec/???????=.md` that `vscode/package.json` declares. `GraphProject` coordinates the backend, the planning of document edits and the watchers of one project, and `GraphView` holds the focus, the cameras and the comparison of one view. A node tab stays bound to its file, a neighbor opens in its own file, graph panels and comparison panels are independent of each other, and the raw text is directly accessible.

`editor_request` in `src/specspec/editor.py` writes nothing: it validates the paths, the text and the size of the overlaid documents, plans one edit of an existing file and returns the diagnostics of the graph. `ProjectDocuments` in `graph-ui-common/host/documents.cjs` runs reading, planning and applying one after another, compares the version and the text of the document around the `WorkspaceEdit`, and refuses a change through the writer while any specspec document of the project has unsaved changes. The text of a buffer without a file is validated before it is left out, and an edit to an absent file fails.

Save, autosave, undo, redo and the recovery of unsaved documents in VS Code persist the `TextDocument`. Each view keeps a backup of form text that is not applied yet, and recovering it is an explicit step. The handling of typing and of sequence numbers, which both editors share, keeps newer input and the text cursor when an acknowledgement from a peer view arrives late. Errors of the executable, of workspace trust and of startup are reported. A node-file editor holds its project during the check of the command line and the first read, and releases the project's watchers and command-line client when either fails.

The tests cover races, the repair of an invalid buffer, the actions of a bound editor, the synchronization and the separate cameras of split views, independent tabs, and saves of CRLF and Unicode text through VS Code.

The extension declares that it runs on the workspace host, which covers real file systems on remote machines. It uses the shared reads that check document versions, the first read of a node-file editor as initial context and the delivery of the working graph before its comparison. The logging of loading phases and the qualification of remote connections are opt-in, and each reports what it covered.

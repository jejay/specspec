---
id: _ANZHCw=
type: implementation
parents:
- GQdmCrA=
- YOPhqYc=
- LvYBN_4=
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
- path: docs/native-editors.md
- path: electron/main.cjs
- path: branding/activity-icon.svg
- path: docs/node-canvas.md
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
- path: vscode/package-lock.json
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
# Adapt VS Code documents and panels to the shared graph

`GraphEditors` contributes `**/_specspec/???????=*.md`; `GraphProject` coordinates
backend/document planning and watchers; `GraphView` owns independent focus/cameras/
comparisons. Node tabs stay bound to their resource, neighbors open their files,
project/revision panels remain independent and raw text is directly accessible.

Python's non-writing `editor_request` validates overlay paths/text/size, plans one
existing-file edit and returns graph diagnostics. `ProjectDocuments` serializes
read/plan/apply, compares versions/text around native WorkspaceEdit and protects
project-wide dirty documents during managed mutations. Missing-buffer text is
validated before omission; absent-resource edits fail.

Native Save/autosave/undo/redo/dirty recovery persist TextDocuments. Per-view backups
retain unapplied form text with explicit recovery. Shared typing/sequence handling
preserves newer input and caret against late peer acknowledgements. Tests cover
races, invalid-buffer repair, bound actions, split synchronization/cameras, independent
tabs and CRLF/Unicode native saves. Executable/trust/startup errors are reported.

---
id: tyygZV8=
type: implementation
parents:
- EXGxivM=
- -DClehg=
sources:
- path: graph-ui-common/view.cjs
- path: graph-ui-common/media/graph.css
- path: graph-ui-common/media/graph.js
- path: graph-ui-common/test/graph.test.cjs
- path: graph-ui-common/test-host/ui.cjs
- path: graph-ui-common/test-host/platform.cjs
- path: vscode/src/view.ts
- path: vscode/src/extension.ts
- path: vscode/test/extension.test.cjs
- path: electron/main.cjs
---
# Render the compact toolbar and save the focused form by keyboard

The common HTML shell in `graph-ui-common/view.cjs` groups the symbol, which has an accessible name, with the revision label, renders Refresh as an SVG icon button with an accessible name and takes an option that shows or hides the project picker. The typed wrapper `vscode/src/view.ts` passes that option on, and `vscode/src/extension.ts` hides the picker in graph panels and in node-file editors. The desktop app in `electron/main.cjs` keeps the picker and its project shortcut and runs without a menu bar.

The renderer in `graph-ui-common/media/graph.js` captures Ctrl+S and Command+S before the keymaps of the text field and before the forwarding of webview shortcuts, and submits the form through the same enabled Save control while a node is focused. The submit handler of the form applies the restrictions of the button. The request carries the current text, the parents, the sources and the original node, and for a VS Code document its version and edit sequence, and it takes the same way through the session, the planner and the saving as a click on Save. An open modal dialog, a draft in the overview and a repeated key cause no further save. The project button is wired only where it exists, so the renderer initializes as well when VS Code leaves the button out.

The shell and the renderer keep the area beneath the toolbar for legends and for diagnostics about operation. The details of changes in linked source files are in the reports of the command line. DOM tests cover an empty set, a single change and a larger set of source changes in the shells of both editors, together with the revision text, the diagnostics and the source badges on nodes.

DOM tests in `graph-ui-common/test/graph.test.cjs` cover the toolbar, the place of the live comparison label, the content of keyboard saves, new nodes, the metadata of VS Code documents, the behavior while a request is pending, after an error and on retry, and the disabled states. The adapter tests in `vscode/test/extension.test.cjs` verify that the picker is left out and that VS Code saves a bound document. Probes in the installed editors, shared through `graph-ui-common/test-host/ui.cjs` and `graph-ui-common/test-host/platform.cjs`, check the toolbar and an actual Ctrl+S against the independent Gantt history, and Command+S on macOS is covered by synthetic events.

The keyboard probes wait until Save is enabled after the comparison has loaded, then send one shortcut and verify exactly what was persisted, within the regular deadlines and under the regular restrictions of read-only and loading views. The startup probes check the blocking screen for a missing command line, retry, explicit initialization, Git and the appended agent instructions, and the complete suites on an existing graph follow them. The probes in the installed editors run on Windows, and graphical runs on physical macOS and Linux machines are unqualified.

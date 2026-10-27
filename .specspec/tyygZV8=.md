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
- path: docs/node-canvas.md
- path: docs/investigations/header-identity.md
---
# Render compact host chrome and submit focused forms by keyboard

The common HTML shell groups an accessible optical symbol and revision label,
renders an accessible SVG Refresh button and accepts an explicit project-picker
option. The typed VS Code wrapper disables that picker for both project and native
file views; Electron retains its picker and project shortcut without a menu bar.

The shared renderer captures Ctrl/Command+S before editor keymaps and webview
forwarding, submitting the same enabled Save control in focused editing. The form
submit guard shares button restrictions. Current target text, parents, sources,
original-node context and native document version/edit sequence use the existing
session, planner and persistence paths. Modal dialogs, overview drafts and repeated
keys do not trigger extra saves. Optional project-button wiring leaves renderer
initialization intact when VS Code omits the element.

The shell and renderer reserve the area beneath the toolbar for legends and
operational diagnostics. CLI reports provide linked source-file change details.
DOM regressions cover empty, singular and larger source
change sets in both host shells while preserving revision text, diagnostics and
node-level source badges.

DOM regressions cover chrome, live comparison placement, keyboard payloads, new
nodes, native document metadata, pending/error/retry behavior and disabled states.
VS Code adapter tests verify picker omission and native Save ownership. Shared
installed-host probes check header chrome and actual Ctrl+S against independent
Gantt history; macOS Command behavior retains synthetic-event coverage.

Installed-host keyboard probes wait for the established enabled Save state after
provisional loading, then send one shortcut and verify exact persistence. They do
not extend deadlines or bypass read-only/loading restrictions. Startup probes check
CLI blocking, retry, explicit initialization, Git and appended instructions before
the complete existing-graph suites. Current execution evidence remains scoped to
Windows hosts; physical macOS and Linux graphical execution remain unqualified.

---
id: IkFelpQ=
type: implementation
parents:
- 3SfTeOo=
- fdB9ZLM=
- ALlkmT0=
sources:
- path: .github/workflows/ci.yml
- path: electron/README.md
- path: electron/launch.cjs
- path: electron/main.cjs
- path: package-lock.json
- path: electron/preload.cjs
- path: electron/renderer.js
- path: electron/scripts/build.cjs
- path: electron/security.cjs
- path: electron/store.cjs
- path: electron/test-host/run.cjs
- path: electron/test/launch.test.cjs
- path: electron/test/security.test.cjs
- path: electron/theme.css
- path: graph-ui-common/test-host/platform.cjs
- path: graph-ui-common/test-host/ui.cjs
---
# Host the shared graph in an authorized Electron window

`main.cjs` owns authorized project selection, trusted CLI launch settings, watcher/
session lifecycle and local asset protocol. `security.cjs` validates senders/messages
and constrains requests/navigation. Sandboxed isolated preload exposes a fixed
port; renderer scripts use shared graph/session assets. Native menus/dialogs supply
normal editing, revision selection and destructive/overwrite confirmation.

`launch.cjs` captures path-bearing executable settings relative to the launch
folder, keeping absolute/PATH meanings across project cwd changes. `store.cjs`
retains bounded project-scoped presentation/drafts and protects corrupt state bytes.
Build/package scripts include shared runtime, icons and project/vendor licenses.

Unit tests check launch/state/security boundaries; isolated installed-host tests
check actual managed saves, draft reload, source/revision views, blocked requests
and shared canvas/paint/native-form invariants. Runtime prerequisites are external
Python/Git and a trusted local launch/project selection.

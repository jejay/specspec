---
id: 9a9b374d-c3cf-47af-a377-cd19ff9e6ec4
type: implementation
parents:
- 449d5e44-2d5f-4c30-b4f3-9207b21b6286
- 037c4383-1934-4181-96e5-9fc3b2958e2f
- a1595f98-cae9-4593-aae9-baff7789b435
sources:
- path: electron/main.cjs
  symbol: authorized main-process host and shared session
- path: electron/preload.cjs
  symbol: fixed sandboxed context-bridge port
- path: electron/security.cjs
  symbol: asset/sender/message allowlists
- path: electron/store.cjs
  symbol: bounded project-scoped drafts, protected bytes and atomic file replacement
- path: electron/renderer.js
  symbol: revision dialog and graph port; no renderer fork
- path: electron/theme.css
  symbol: VS Code dark surface/Git defaults
- path: electron/scripts/build.cjs
  symbol: exact shared assets/runtime and project license
- path: electron/test/security.test.cjs
  symbol: six state/security regressions
- path: electron/test-host/run.cjs
  symbol: real isolated save/stale/reload/history checks
- path: electron/package-lock.json
  symbol: pinned Electron/packager dependency tree
- path: electron/README.md
  symbol: Linux/Windows run/package instructions and boundaries
- path: graph-ui-common/test-host/ui.cjs
  symbol: one shared real canvas harness
- path: graph-ui-common/test-host/platform.cjs
  symbol: real themed A/M/D, sandbox and UI mutations
- path: .github/workflows/ci.yml
  symbol: target Linux/Windows smoke/package matrix
managed_hash: 34c69f0ea61579939cfed0da87fdd99b6c643a8df043f9613b8cd3b7e2f87321
---
# Run the shared graph in an isolated local Electron window

The initial Electron 44.6.0 shell builds the same shared renderer/template/session
bytes as VS Code and bundles local Dagre/D3 with 12 license notices. Its custom
asset allowlist serves only application resources; navigation, popups, remote
requests and permissions are denied. Sandboxed/context-isolated preload exposes
only graph messaging, project-scoped state and revision-result functions, never
Node/FS/spawn/general IPC. Main-frame ownership, exact app URL, generation tokens,
bounded messages and authorized roots guard IPC. The main process fixes CLI launch
configuration and delegates all writes to the bounded Python API-2 session.
Explicit launch paths authorize the local launcher; folder selection asks Trust
and Open. Native confirmation protects retire/restore/migrate. Native inline
forms, keyboard edit menu and a bounded revision dialog retain normal editing.
Presentation/drafts live outside canonical data, protect corrupt bytes, preserve
original fingerprints and do not evict saved drafts. Reload receives a fresh
snapshot and restores dirty content; scope/generation prevent old-root messages
from reaching a new root. No graph files are staged/committed or hook installed.

Six desktop state/security tests passed. A real Windows Electron run on a cloned
CLI-managed/Git graph passed the shared geometry/camera/hover/metric/native-form
suite, actual A/M/D and live theme paint, no renderer Node, blocked requests/popups,
a real UI save, stale backend rejection, dirty draft reload, and actual historical/
workspace switching. Acknowledgements check tokens, modern fingerprints and full
membership. The harness selects the main renderer port, not the isolated preload
world; asynchronous CLI/Git completion is polled rather than assuming five seconds.
Desktop screenshots were inspected. A portable Windows x64 package was built with
packager 20.3.0, and the pinned dependencies audit with no known findings. The actual packaged Windows executable also passed the full real UI/save/stale/reload/history suite on a 66-node target/67-node display fixture. ASAR inspection verifies exact shared runtime bytes, local vendor assets/icons and project/dependency licenses, excluding diagnostics/tests/node_modules. VSIX inspection verifies the same boundaries. This is actual portable startup evidence, not a Linux or installer claim.

Linux is targeted by platform-neutral code and configured CI/Xvfb/sandbox setup;
no local Linux or completed remote CI execution is claimed. Python/Git remain
external. No installer/signing/updater, bundled Python, credential service or
Claude Code/Codex connector exists yet. Native dialog/manual/accessibility/device/
large-graph/performance/adversarial-filesystem and full power-loss guarantees are
not claimed by DOM-dispatched smoke tests or these initial security boundaries.

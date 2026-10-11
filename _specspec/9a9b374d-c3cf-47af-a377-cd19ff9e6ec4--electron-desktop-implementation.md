---
id: 9a9b374d-c3cf-47af-a377-cd19ff9e6ec4
type: implementation
parents:
- 449d5e44-2d5f-4c30-b4f3-9207b21b6286
- 037c4383-1934-4181-96e5-9fc3b2958e2f
- a1595f98-cae9-4593-aae9-baff7789b435
sources:
- path: .github/workflows/ci.yml
  symbol: target Linux/Windows smoke/package matrix
- path: electron/README.md
  symbol: Linux/Windows run/package instructions and boundaries
- path: electron/main.cjs
  symbol: authorized main-process host and shared session
- path: electron/package-lock.json
  symbol: pinned Electron/packager dependency tree
- path: electron/preload.cjs
  symbol: fixed sandboxed context-bridge port
- path: electron/renderer.js
  symbol: revision dialog and graph port; no renderer fork
- path: electron/scripts/build.cjs
  symbol: exact shared assets/runtime and project license
- path: electron/security.cjs
  symbol: asset/sender/message allowlists
- path: electron/store.cjs
  symbol: bounded project-scoped drafts, protected bytes and atomic file replacement
- path: electron/test-host/run.cjs
  symbol: real isolated save/stale/reload/history checks
- path: electron/test/security.test.cjs
  symbol: six state/security regressions
- path: electron/theme.css
  symbol: VS Code dark surface/Git defaults
- path: graph-ui-common/test-host/platform.cjs
  symbol: real themed A/M/D, sandbox and UI mutations
- path: graph-ui-common/test-host/ui.cjs
  symbol: one shared real canvas harness
- path: electron/launch.cjs
  symbol: resolveExecutable; launch-directory path capture
- path: electron/test/launch.test.cjs
  symbol: three relative/absolute/PATH/cwd regressions
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


## Launch-relative interpreter correction

electron/launch.cjs resolves path-bearing --python/SPECSPEC_PYTHON/SPECSPEC_COMMAND settings once from the trusted launch directory. Absolute executables and bare PATH names keep their meaning; per-project subprocess cwd cannot reinterpret ../.venv paths. Nine desktop tests now pass, including three launch regressions: launch versus project roots, absolute/PATH/spaced paths, and a real subprocess from a different cwd. The real Electron host harness now supplies a launch-relative interpreter and a different temporary graph root; the full Windows canvas/save/stale/reload/history suite passed. The portable package is rebuilt for this fix; prior absolute-path-only smoke evidence did not cover the reported case. Linux execution remains unverified.


## Hash-free Markdown synchronization revision

The later manual-edit intention and separate hash-free/watcher conclusion supersede
all earlier API-2/fingerprint/stale-hash claims in this record. Current code uses
API/format 3, no managed_hash or fingerprint gate, and permits valid manual edits.
Original detailed test counts and packaged-host evidence above remain historical,
not claims of re-running every old package or platform against this revision.

GraphSession coalesces watcher events, retries failed reads twice, compares records
directly and validates current files before UI writes. Render sequence/full-membership
checks remain without fingerprint acknowledgements. Dirty drafts retain original
node records/caret/camera; unrelated changes permit saving, same-node overwrites ask
confirmation, and deletion/invalid files preserve copyable drafts. Invalid reloads
mark the last valid graph out of date and disable mutations until a valid reload.
VS Code watches directory/files; Electron's shared GraphWatcher also watches the
parent and reattaches after canonical-directory recreation. Optional configurable
polling defaults to zero/off and is disposed with sessions. No silent fallback,
universal event-delivery guarantee or adversarial race-free writes are claimed.

The independent Gantt working graph was migrated without changing body/relationship
semantics. Its original CLI receipts/Git commits are retained verbatim. The history
verifier now reconstructs records and compares actual contents directly; archived
hash strings are opaque receipt labels, not a current hash algorithm or edit gate.
See the separate current implementation record for source links and final checks.

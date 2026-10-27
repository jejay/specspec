---
id: HZHjxQ8=
type: implementation
parents:
- TpFMeZc=
- 0aNDHfQ=
- yEoFkOE=
- sxxzsrk=
sources:
- path: graph-ui-common/host/session.cjs
- path: graph-ui-common/host/git-watch.cjs
- path: graph-ui-common/media/graph.js
- path: graph-ui-common/test/session.test.cjs
- path: graph-ui-common/test/graph.test.cjs
- path: graph-ui-common/test/loading.test.cjs
- path: graph-ui-common/test-host/ui.cjs
- path: graph-ui-common/test-host/platform.cjs
- path: vscode/test-host/run.cjs
- path: electron/test-host/run.cjs
- path: graph-ui-common/test/git-watch.test.cjs
- path: vscode/src/extension.ts
- path: vscode/test/extension.test.cjs
- path: graph-ui-common/host/client.cjs
- path: graph-ui-common/host/reads.cjs
- path: graph-ui-common/test/client.test.cjs
- path: src/specspec/api_transport.py
- path: src/specspec/cli.py
- path: tests/test_api_transport.py
- path: vscode/src/bridge.ts
- path: electron/main.cjs
- path: docs/loading.md
- path: docs/architecture.md
- path: docs/investigations/host-smoke.md
---
# Implement responsive source and metadata read scheduling

The shared session gives source previews an independently coalesced read-only lane,
freezes displayed comparison commits and suppresses obsolete replies. Automatic graph
reads and independent Spotlight notifications have separate refresh work; explicit
Refresh, initial loading and polling keep list recovery and baseline semantics.

Git watch discovery uses asynchronous shell-free bounded execution and coalesces
notifications while reconciling current private/common directories. Disposal prevents
late adoption. Session, renderer and watcher regressions hold background work open,
exercise latest-request and navigation races, and retain mutation/native boundaries.
Complete installed-host suites exercise actual source previews, canvas/backchannels,
watcher recovery, native lifecycle and persisted reload/revision switching.

Both adapters use the shared HEAD/ref watcher, with canonical text watched
independently. Index stat-cache updates and Git-extension status notifications
leave working presentation unchanged; explicit staged operations remain fresh.

Project-scoped bounded API channels reuse interpreter lifetime, with independent
source previews, current per-request reads and guarded disposal/failure semantics.

Spotlight-specific adapter read-count tests hold independent initial Git discovery
pending until teardown. Separate controlled-clock regressions exercise that valid
late discovery hint and its graph refresh. This isolates event causes without
suppressing production notifications or extending debounce/deadline budgets.

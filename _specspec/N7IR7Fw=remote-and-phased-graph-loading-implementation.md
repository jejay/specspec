---
id: N7IR7Fw=
type: implementation
parents:
- uY3KPsM=
- 3V6SdSA=
- VDss3KM=
- FJj-9xY=
sources:
- path: vscode/package.json
- path: vscode/src/extension.ts
- path: graph-ui-common/host/documents.cjs
- path: graph-ui-common/host/session.cjs
- path: graph-ui-common/host/cli.cjs
- path: graph-ui-common/media/graph.js
- path: graph-ui-common/test/loading.test.cjs
- path: vscode/test/extension.test.cjs
- path: vscode/test/bridge.test.cjs
- path: vscode/test-host/remote.cjs
- path: docs/remote-workspaces.md
- path: docs/loading.md
- path: graph-ui-common/host/reads.cjs
- path: graph-ui-common/host/wire.cjs
- path: graph-ui-common/test/wire.test.cjs
- path: electron/main.cjs
---
# Adapt workspace-host execution and working-first graph delivery

The VS Code manifest declares workspace placement, real-filesystem capability,
and opt-in loading diagnostics. The adapter uses host-file resources, remote
executable settings, VS Code asset routing/messages and native persistence.
ProjectReads shares identical in-flight reads in Electron and VS Code with
before/after document/generation stamps, isolated view payloads and bounded verified
baseline hints. ProjectDocuments adds native planning and persistence coordination. Native bootstrap
supplies initial usable context while preserving asynchronous editor wiring.
GraphSession first renders explicit provisional working context, then a fresh
comparison; historical views retain their selected read-only comparison. The renderer
preserves drafts/caret/camera and restricts provisional project controls. Loading
records measure host phases and client rendering with their respective clocks.

Subprocess failures after a mutation starts explain an unconfirmed outcome for
current-state inspection; actions are not automatically replayed. Adapter/session
regressions cover shared/bootstrap races, delayed comparisons, disposal, trust,
resource boundaries, bound native documents and lost replies. The opt-in remote
module checks actual workspace-host placement, native overlays, rendered membership
and source objects on a disposable history clone. Transport qualification is reported
from dispatched runs individually; setup and investigation guides expose its limits.

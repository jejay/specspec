---
id: GG_koyg=
type: implementation
parents:
- -UedVEw=
- cpFRqIM=
- nIj9fmE=
sources:
- path: graph-ui-common/host/reads.cjs
- path: graph-ui-common/host/documents.cjs
- path: graph-ui-common/host/session.cjs
- path: graph-ui-common/host/cli.cjs
- path: graph-ui-common/host/wire.cjs
- path: graph-ui-common/test/loading.test.cjs
- path: graph-ui-common/test/wire.test.cjs
- path: graph-ui-common/test/session.test.cjs
- path: graph-ui-common/test-host/platform.cjs
- path: electron/main.cjs
- path: vscode/src/extension.ts
- path: vscode/test/bridge.test.cjs
- path: vscode/test/extension.test.cjs
- path: vscode/test-host/remote.cjs
- path: docs/loading.md
---
# Share current graph reads while preserving host persistence owners

ProjectReads coordinates optional-overlay application reads, shared in-flight work,
actual document/generation stamps, verified bounded baseline hints, bootstrap reuse
and disposal. Both hosts supply this same coordinator; historical targets bypass
working buffers. ProjectDocuments extends it for guarded native planning/application.
GraphSession renders provisional working context then a complete comparison and uses
one shared read for refreshes rather than an export/diff chain.

The bounded bridge rejects incompatible protocol versions and expands compact data
once into complete revision-local renderer records. Deleted HEAD bodies/relationships
remain copyable D records through staging; fresh committed baselines remove them.
Source preview/capture uses typed non-writing application requests. Managed writes
still preflight saved files and retain native dirty guards, reviewed deletion plans,
locking/original-byte/recovery rules and unknown-outcome reporting without replay.

Shared tests cover compact reconstruction, stale/coalesced reads, saved-only Electron
reads and hints, late bootstrap results, provisional/historical delivery and complete
membership acknowledgements. Both real-host suites exercise graph/source/watch/form/
geometry and cascade ghost lifecycles; Git-paint probes wait for the completed
comparison rather than misclassifying provisional cards. Native Save/undo and managed
writer lifecycles remain separate. Presentation and polling/deadline contracts retain
their established owners.

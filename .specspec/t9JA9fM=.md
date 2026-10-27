---
id: t9JA9fM=
type: implementation
parents:
- YJjtPzc=
- LjyJ0Ow=
sources:
- path: graph-ui-common/host/session.cjs
- path: graph-ui-common/view.cjs
- path: graph-ui-common/media/graph.js
- path: vscode/src/extension.ts
- path: electron/main.cjs
- path: vscode/package.json
- path: electron/package.json
- path: src/specspec/cli.py
- path: graph-ui-common/host/startup.cjs
- path: graph-ui-common/test/startup.test.cjs
- path: tests/test_cli_stdin.py
- path: docs/investigations/owner-experience.md
- path: graph-ui-common/test-host/startup.cjs
- path: electron/test-host/startup.cjs
- path: electron/test-host/run.cjs
- path: vscode/test-host/run.cjs
- path: vscode/test-host/smoke.cjs
---
# Implement shared startup gates and lowercase installed products

The common session/renderer displays explicit CLI-check, install/retry, project
selection, initialization and ready states. Trusted adapters supply a bounded CLI
probe and real project inspection, preserve workspace trust, and route explicit init
through the managed writer before fresh read adoption. Electron removes its menu
bar while retaining project selection controls and an explicit keyboard shortcut.
Package metadata and runtime labels identify the independently installed products.
Unit and installed-host probes cover missing CLI, no graph, initialization and retry
alongside normal graph and native-document persistence.

A static CLI capability probe prevents an older same-envelope CLI from silently
ignoring a managed stdin body. Missing modules, incompatible capabilities and
project repair failures retain distinct blocking diagnostics.

---
id: iER7QwM=
type: implementation
parents:
- evfMtUM=
- 1aSOZOs=
- yJnnDfM=
- FU5NaYc=
sources:
- path: .github/workflows/ci.yml
- path: .vscode/launch.json
- path: .vscode/tasks.json
- path: AGENTS.md
- path: README.md
- path: branding/README.md
- path: docs/node-canvas.md
- path: docs/own-spec.md
- path: electron/README.md
- path: electron/test-host/run.cjs
- path: example/gantt/README.md
- path: example/gantt/history/verify.py
- path: graph-ui-common/host/session.cjs
- path: graph-ui-common/package.json
- path: graph-ui-common/test-host/ui.cjs
- path: graph-ui-common/view.cjs
- path: specspec-dev.code-workspace
- path: tests/test_gantt_example.py
- path: tests/test_ids.py
- path: tests/test_repository_spec.py
- path: vscode/.vscode/launch.json
- path: vscode/scripts/build-webview.cjs
- path: vscode/test-host/run.cjs
- path: vscode/test-host/smoke.cjs
- path: vscode/test-host/ui.cjs
- path: example/gantt/history/checkout.py
- path: example/gantt/history/gantt.bundle
- path: graph-ui-common/test-host/fixture.cjs
- path: tests/test_example_checkout.py
- path: tests/test_gantt_git.py
- path: tests/test_repository_docs.py
- path: docs/architecture.md
- path: docs/architecture.svg
- path: .gitattributes
- path: .gitignore
---
# Validate and document the working graph and planning process

CI and repository tests validate this current graph, complete agent context,
source references and manual-edit behavior. Development launches open the working
specification. `docs/own-spec.md` indexes current intentions, choices and realization
links. `AGENTS.md` supplies owner/tandem/agent/implementation planning instructions.
The graph defines current binding behavior; Git carries revision rationale.

The offline architecture Markdown/SVG maps runtime/persistence/test ownership with
local links and accessible scoped resources. Artifact tests check exact brand
imports/non-text attributes and narrowly ignored machine-local settings with shared
launch files tracked. Independent example histories supply temporal integration;
local experiments and diagnostic/recovery state remain preserved.

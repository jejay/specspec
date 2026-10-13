---
id: oFOaAVo=
type: implementation
parents:
- 83D9YWw=
sources:
- path: .github/workflows/ci.yml
- path: AGENTS.md
- path: README.md
- path: docs/own-spec.md
- path: electron/test-host/run.cjs
- path: example/gantt/AGENTS.md
- path: example/gantt/README.md
- path: example/gantt/history/WALKTHROUGH.md
- path: example/gantt/history/checkout.py
- path: example/gantt/history/gantt.bundle
- path: example/gantt/history/revisions.json
- path: example/gantt/history/verify.py
- path: example/gantt/test/browser.cjs
- path: graph-ui-common/test-host/fixture.cjs
- path: tests/conftest.py
- path: tests/test_example_checkout.py
- path: tests/test_gantt_example.py
- path: tests/test_gantt_git.py
- path: vscode/test-host/run.cjs
---
# Create independent example workspaces without overwriting experiments

`checkout.py` materializes the complete bundle externally with LF configuration.
It resolves/refuses development-worktree or existing destinations, atomically claims
a new folder and retains failed/partial clones. Existing manual clones keep their
local experiments. Tests and CI use fresh disposable standalone repositories.

Python history/Git fixtures and both real hosts share this complete-history checkout
path. They preserve refs/ancestry/index and add only disposable worktree cues.
Focused native/nested tests retain their small graphs. The history verifier checks
all revisions and final runtime/graph agreement; browser reload checks wait for a
fresh fully loaded document. Current recipe/commands are in the example guides.

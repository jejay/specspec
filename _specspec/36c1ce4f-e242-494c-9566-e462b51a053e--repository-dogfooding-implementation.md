---
id: 36c1ce4f-e242-494c-9566-e462b51a053e
type: implementation
status: proposed
parents:
- 407b1a12-8984-4c99-9b7f-b920da33e31b
- 955b905a-6220-4d5c-b0ca-fab86b6b6db8
sources:
- path: .github/workflows/ci.yml
- path: .vscode/launch.json
- path: .vscode/tasks.json
- path: AGENTS.md
- path: README.md
- path: docs/own-spec.md
- path: specspec-dev.code-workspace
- path: tests/test_repository_spec.py
- path: vscode/.vscode/launch.json
- path: vscode/test-host/run.cjs
- path: vscode/test-host/smoke.cjs
- path: vscode/test-host/ui.cjs
- path: docs/node-canvas.md
- path: vscode/scripts/build-webview.cjs
managed_hash: 7aef9b6fc07d57c007f702b38cdaca5942c356aec8575830ea346ea71cea08de
---
# Check and document this repository own graph

The Python CI matrix runs the packaged validator against this repository graph
with warnings treated as failures. Repository-level tests inspect the real graph,
exercise agent context, and demonstrate unmanaged-edit detection in memory and
staged copies in a disposable Git repository. They do not mutate the checkout or
freeze future approval decisions.

The README and graph tour provide entry points; AGENTS.md records the managed
editing/review workflow. The development launches open specspec-dev.code-workspace
in an isolated profile and pass the local Python interpreter explicitly, without
relying on PATH or focusing a normal VS Code window. Normal launches retain trust;
only the disposable automated host test disables it.

The installed-VS-Code test now also drives the actual webview through a loopback
Chromium debugger. On Windows it has verified workspace loading, focused inline
editing presentation, back navigation, semantic color modes, root parent controls,
viewport-independent LR layout, cursor-anchored wheel zoom, drag panning,
curve/content clearance, and resized/scaled side-port endpoints. Optional screenshot
capture has been exercised and the resulting focused/overview images inspected. The test runner uses Node 22+ and a
temporary profile; it does not stage, commit, install hooks, or write node changes.
Remote CI and full manual mutation/revision-picker interactions remain unverified.

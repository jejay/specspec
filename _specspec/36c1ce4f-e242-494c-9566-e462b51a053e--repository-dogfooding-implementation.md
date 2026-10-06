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
- path: docs/node-canvas.md
- path: docs/own-spec.md
- path: specspec-dev.code-workspace
- path: tests/test_repository_spec.py
- path: vscode/.vscode/launch.json
- path: vscode/scripts/build-webview.cjs
- path: vscode/test-host/run.cjs
- path: vscode/test-host/smoke.cjs
- path: vscode/test-host/ui.cjs
managed_hash: 637a8d3d426b19c7714d79c66abdad21aea0bf2bd1e40bc2c198f4e708e03dac
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

The installed-VS-Code test drives the actual webview through a loopback Chromium
debugger. On Windows it has verified workspace loading, inline focused editing,
back navigation, semantic colors, root parent controls, viewport-independent LR
layout, cursor-anchored zoom, and panning. The latest correction verifies every live
node's earliest source rank and compact vertical origin neighborhood, minimum screen stroke/head strength at 12 percent zoom,
no endpoint circles, tangent-aligned head bases, actual multiple-depth parent
relationships, and sampled painted-stroke clearance after resizing a textarea.
Screenshot capture has been exercised and the resulting overview/minimum-zoom/
focused/multiple-parent images inspected. The runner uses Node 22+ and a disposable
profile; it does not stage, commit, install hooks, or write canonical changes.

53 Python tests, 59 editor tests, TypeScript compilation, Ruff and graph validation
with warnings as errors have passed locally. Remote CI and full manual mutation/
revision-picker workflows remain unverified. Working evidence is not approval of
the related technical proposals.

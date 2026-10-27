---
id: przmxmo=
type: implementation
parents:
- Q7FDb7A=
- MmfPuhY=
- 1ev9uZo=
sources:
- path: package.json
- path: package-lock.json
- path: pyproject.toml
- path: tools/release.py
- path: tools/build_icon.py
- path: vscode/scripts/package.cjs
- path: vscode/README.md
- path: vscode/test-host/install.cjs
- path: vscode/test-host/run.cjs
- path: vscode/test-host/smoke.cjs
- path: vscode/test/install.test.cjs
- path: electron/scripts/package.cjs
- path: electron/test/package.test.cjs
- path: electron/test-host/run.cjs
- path: graph-ui-common/scripts/build.cjs
- path: graph-ui-common/test/build.test.cjs
- path: src/specspec/model.py
- path: tests/test_release.py
- path: tests/test_cli_literal_layout.py
- path: tests/test_repository_docs.py
- path: README.md
- path: CONTRIBUTING.md
- path: CHANGELOG.md
- path: docs/install.md
- path: docs/releasing.md
- path: docs/platforms.md
- path: docs/investigations/release-0.1.md
- path: branding/identity.sha256.json
- path: branding/specspec-logo-light.svg
- path: branding/specspec-logo-dark.svg
- path: branding/specspec-logo-light.png
- path: branding/specspec-logo-dark.png
- path: branding/app-icon.ico
- path: .github/workflows/ci.yml
- path: .github/workflows/release-build.yml
- path: docs/investigations/final-newline.md
- path: docs/investigations/owner-experience.md
---
# Build and qualify independent local CLI and visual-host artifacts

The root private npm workspace/lock and scripts install, build and test the shared
renderer, VS Code and Electron adapters. Python metadata builds an isolated global
CLI wheel/source distribution containing the initialization template. Local VSIX
creation packages compiled adapter/common code, assets and dependency notices;
Electron packaging allowlists runtime files, supplies the selected native launcher
and creates a current-platform portable archive. The standard-library release
inspector checks versions, resources, runtime membership, asset/license presence
and archive semantics, then writes artifact digests and a manifest.

README and installation/contribution/host/release guides explain the specification
spectrum before setup, show the selected exact light/dark logo imports, distinguish
normal VSIX installation from developer F5, and explain global CLI/PATH ownership.
The original supplied artwork and local experiments remain preserved.

Fresh isolated uv-tool installs from both wheel and source distribution exercise
Unicode, physical EOL replacement, raw versus logical readings, generated instructions
and preserved owner bytes outside the checkout. Artifact-host probes install the
VSIX in a disposable extensions directory with a separate test controller, and run
the unpacked desktop executable against the isolated global-style CLI. Existing
complete canvas, native-document, source, consent, invalid-graph, watcher, Git,
spotlight and reload suites retain their assertions and production safeguards.
Current startup/naming qualification is recorded in the owner-experience
investigation, with earlier release/audit evidence scoped to its checkpoint. Build
workflows upload artifacts without publication, tags, owner installs or Git writes.

Permission-sensitive Linux archive verification executes on a POSIX filesystem.
Qualification records distinguish the executed Python/archive environment from
unexecuted graphical hosts. The final-newline investigation records the terminator
boundary, filesystem evidence and self-contained Git regression fixtures.

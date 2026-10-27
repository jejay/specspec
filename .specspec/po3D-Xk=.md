---
id: po3D-Xk=
type: implementation
parents:
- qY3YIpQ=
- JYMQE1c=
sources:
- path: .github/workflows/pipy_publish.yaml
- path: pyproject.toml
- path: package.json
- path: package-lock.json
- path: graph-ui-common/package.json
- path: vscode/package.json
- path: electron/package.json
- path: src/specspec/__init__.py
- path: src/specspec/templates/AGENTS.md
- path: tools/release.py
- path: tools/pypi_release.py
- path: tests/test_release.py
- path: tests/test_release_workflow.py
- path: README.md
- path: docs/install.md
- path: docs/releasing.md
- path: docs/remote-workspaces.md
- path: docs/investigations/pypi-0.0.1.md
- path: graph-ui-common/view.cjs
- path: graph-ui-common/media/graph.js
- path: graph-ui-common/test/graph.test.cjs
- path: graph-ui-common/test-host/startup.cjs
- path: vscode/src/extension.ts
- path: vscode/test/extension.test.cjs
---
# Implement aligned PyPI releases and public installation guidance

Python/runtime metadata, all maintained npm packages and their local lock entries
agree on 0.0.1. The release inspector checks that alignment without changing
third-party versions or internal node/protocol contracts. Current user/agent/remote
guides and both startup surfaces recommend the public isolated PyPI installation;
source/wheel alternatives and explicit replacement of older local builds remain.

The manually dispatched pipy_publish.yaml matches repository jejay/specspec and
environment pypi. Its read-only build job verifies expected version, graph/source
consistency, maintained history, lint/tests, exact wheel/sdist contents and fresh
installed CLI behavior. The separate publisher downloads the two verified artifacts
without a project checkout, alone requests OIDC, and uses pinned PyPA tooling with
attestations and strict duplicate handling. Build validation pins Twine 7.0.0 to
match that publisher runtime and support the backend metadata rather than bypassing
strict checks. No local package or ordinary push publishes. Standard-library helpers and regression tests cover version/lock drift,
metadata, unsafe/duplicate/stale artifacts and the identity/source-execution split.

The release procedure explains the signed-identity boundary, exact publisher
settings, dispatch, upgrades, failure/partial-upload inspection and public-index
verification. Executed qualification and actual publication are recorded separately
from workflow declarations in the PyPI release investigation.

The 0.0.1 CLI wheel and source distribution are available from PyPI through the
declared workflow publisher, with public provenance binding their file hashes.
Fresh isolated index and source-distribution installations confirm the shipped CLI
and guide contracts. The release investigation retains exact artifacts, source
revision, run evidence, platform coverage and separate CI-oracle corrections.

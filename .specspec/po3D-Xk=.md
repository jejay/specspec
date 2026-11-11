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
- path: graph-ui-common/view.cjs
- path: graph-ui-common/media/graph.js
- path: graph-ui-common/test/graph.test.cjs
- path: graph-ui-common/test-host/startup.cjs
- path: vscode/src/extension.ts
- path: vscode/test/extension.test.cjs
---
# Check one release version, publish the command line to PyPI by workflow and recommend that installation in guides and editors

`pyproject.toml`, `__version__` in `src/specspec/__init__.py`, the four `package.json` files of the root, `graph-ui-common`, `vscode` and `electron`, and their entries in `package-lock.json` all state the version 0.0.1. The function `version` in `tools/release.py` checks that they agree and changes no file. The versions of third-party packages and the version numbers of the node format and of the protocol are outside this check.

`README.md`, the agent guide in `src/specspec/templates/AGENTS.md`, the startup screen of both graph editors in `graph-ui-common/view.cjs` and `graph-ui-common/media/graph.js` and the fallback page of the extension in `vscode/src/extension.ts` recommend `uv tool install specspec`, the isolated installation from PyPI. Both screens tell the user of a remote VS Code window to install on the workspace host. `README.md` names `pipx install specspec` as the alternative and gives the commands that put `specspec` on the `PATH` and that upgrade it. `CONTRIBUTING.md` describes the installation from a checkout and the build of a wheel for development, and `CHANGELOG.md` says how an older local build is replaced explicitly, with `uv tool install --force specspec`. `tests/test_release_workflow.py`, `graph-ui-common/test/graph.test.cjs`, `graph-ui-common/test-host/startup.cjs` and `vscode/test/extension.test.cjs` assert the recommended command in these places.

`.github/workflows/pipy_publish.yaml` runs on a manual start alone and matches the trusted publisher for the repository `jejay/specspec` and the environment `pypi`. Its build job has read permission and no identity. It checks the expected version, both graphs with their source links, the maintained Gantt history, lint and tests, builds the wheel and the source distribution, verifies their exact contents and runs the command line from a fresh installation of each. The separate publish job downloads the two verified files without a checkout of the project, is the only job that requests the OIDC identity, and uploads with the publishing action of PyPA, pinned to a commit, with attestations and strict handling of duplicates. The build job pins Twine 7.0.0, which matches the runtime of the publishing action and reads the metadata that the build backend writes, so that `twine check --strict` applies in full. A local package and an ordinary push publish nothing.

`tools/release.py` and `tools/pypi_release.py` use the Python standard library alone. `tests/test_release.py` and `tests/test_release_workflow.py` cover versions and lockfile entries that have drifted apart, the metadata of the distributions, unsafe, duplicate and stale artifacts, and the separation of the identity from every step that executes project source.

The release procedure in `CONTRIBUTING.md` names the job that alone receives the identity, the exact settings of the trusted publisher, the manual start with the exact version and the confirmation on the public index with a fresh installation. The commit message of a release records which checks were run and what was published, apart from what the workflow declares.

Version 0.0.1 of the wheel and of the source distribution is on PyPI, published through this workflow as the declared trusted publisher, with public provenance that binds the hashes of both files. Fresh isolated installations from the index and from the source distribution confirm the shipped CLI and guide contracts.

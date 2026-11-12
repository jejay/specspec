---
id: qY3YIpQ=
type: requirement
parents:
- DFS2oJM=
---
# Give all maintained products one release version

The Python project and runtime, the private root npm workspace, the shared UI
workspace, specspec-vscode and specspec-desktop share one release version, recorded
consistently in lockfiles and distribution filenames. Local builds publish nothing; a release publishes the CLI to PyPI and the editor packages as downloads of its GitHub release. Release versions are independent of
internal node/protocol fields and third-party dependency versions.

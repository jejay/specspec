---
id: qY3YIpQ=
type: requirement
parents:
- DFS2oJM=
---
# Give all maintained products one release version

The Python project and its runtime, the private npm workspace at the root, the shared UI workspace, `specspec-vscode` and `specspec-desktop` have one release version. The lockfile records it for each of them, and the file names of the distributions carry it. A build from source and a build of an editor are local artifacts, and publishing one of them needs an authorization of its own. The release version is independent of the version numbers of the node format and of the application protocol, and of the versions of third-party dependencies.

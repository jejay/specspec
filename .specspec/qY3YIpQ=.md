---
id: qY3YIpQ=
type: requirement
parents:
- DFS2oJM=
---
# Give all maintained products one release version

The Python project and runtime, the private root npm workspace, the shared UI
workspace, specspec-vscode and specspec-desktop share one release version, recorded
consistently in lockfiles and distribution filenames. Source and UI builds stay local
until their own publication is authorized. Release versions are independent of
internal node/protocol fields and third-party dependency versions.

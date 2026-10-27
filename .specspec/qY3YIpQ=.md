---
id: qY3YIpQ=
type: requirement
parents:
- DFS2oJM=
---
# Align maintained product versions at 0.0.1

Use 0.0.1 for the Python project and runtime, private root npm workspace, shared
UI workspace, specspec-vscode and specspec-desktop. Their local lockfile records
and versioned distribution filenames agree. Source/UI builds remain private/local
unless their own publication is authorized. Product release versions are separate
from internal node/protocol fields and third-party dependency versions.

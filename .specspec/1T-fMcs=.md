---
id: 1T-fMcs=
type: requirement
parents:
- XV5_rPQ=
---
# Make the initial release straightforward to install and try

Prepare a candid initial release from one source monorepo. People can independently
install the global CLI, build and install the extension into their ordinary VS Code
instance, or build and run the standalone Electron UI. Explain prerequisites,
commands, output locations, upgrades and troubleshooting without requiring knowledge
of the development harness. The VS Code package is distributed locally as a VSIX;
Marketplace publication remains a separate owner decision. Building is distinct
from publishing, signing, tagging or committing.

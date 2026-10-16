---
id: uY3KPsM=
type: requirement
parents:
- CmZafVM=
- GQdmCrA=
---
# Execute through VS Code's workspace host and authenticated transport

Declare the Node extension a workspace extension and describe real-filesystem
capability accurately. Install its VSIX and Python 3.11+/matching API-6 application
on the executing workspace host; use remote machine settings for its executable.
VS Code owns SSH/tunnel authentication, resource routing and connection lifecycle.
Bundled webview assets use asWebviewUri and dynamic content uses message passing.

Treat file URIs on the executing host as its filesystem resources. VS Code normally
maps remote URIs to file URIs inside that host; preserve actionable rejection for
virtual resources and client-local resources presented to a remote host. Verify
native document membership and project discovery there. Report execution placement,
dependency and trust failures with usable diagnostics. Retain recovery and original
input on failed delivery; reconnect reads current state before further mutations.
Destructive requests receive one deliberate execution, with unknown outcomes
reported for inspection rather than automatically replayed.

Provide remote setup and an opt-in installed-host qualification path. Report actual
SSH, desktop tunnel and browser tunnel coverage individually, including environment
limitations. Virtual repository browsing has its own execution requirement.

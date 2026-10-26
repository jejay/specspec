---
id: 3SfTeOo=
type: requirement
parents:
- YOPhqYc=
---
# Use an isolated Electron shell and explicit local authorization

Use Electron for the standalone Linux/Windows host. A sandboxed, context-isolated
renderer with `nodeIntegration` disabled receives a fixed preload messaging/state
port. The main process authorizes selected local projects, fixes the CLI executable
from trusted launch configuration, validates IPC sender/messages and delegates graph
operations to the shared Python/session authority. Restrict navigation, popups,
requests and permissions to the local application boundary.

Use native project/destructive/overwrite confirmations, bounded revision input and
project-scoped presentation/draft storage with protected corrupt bytes. Recheck
current authorization and files and surface launch/process/render errors.

Resolve explicit executable paths once from trusted launch options/environment
against the launch directory. Absolute paths retain their meaning; bare names use
PATH. Selected project cwd determines project operations. Python and Git are external
prerequisites; delivery targets are a portable desktop app and local host integration.

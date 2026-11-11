---
id: 3FThKz4=
type: requirement
parents:
- PL1IogE=
---
# Keep the shared graph editor adaptable to the workflows of coding agents

The shared graph editor can be adapted to the workflows of Claude Code and OpenAI Codex through a further adapter. In every adapter the Python tool validates the graph and performs its changes. The adapters that exist are the command line, the VS Code extension and the desktop app. The transport of an agent, the boundary of its credentials, its authorization and its lifecycle are left open here: each is specified as a conclusion of its own, and a connector is built on that specification.

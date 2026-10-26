---
id: nxNOTwc=
type: implementation
parents:
- J8H7P74=
sources:
- path: src/specspec/templates/AGENTS.md
- path: src/specspec/workspace.py
- path: src/specspec/cli.py
- path: src/specspec/output.py
- path: pyproject.toml
- path: tests/test_initialization.py
- path: tests/test_release.py
- path: docs/agents.md
- path: docs/install.md
- path: docs/investigations/release-0.1.md
---
# Bundle and safely initialize current project agent instructions

The package template combines conceptual relationships, meaningful granularity,
owner/agent phases and practical current CLI workflows. Its documented owner inputs
are drafting sources, not runtime dependencies. Hatchling includes the template in
wheel/source distributions; initialize reads package resources independently of
checkout paths. CLI receipts report instruction creation or preservation.

Initialization validates the candidate, stages node/guide bytes, records known
absence/replacement states and publishes the graph under the existing workspace
lock. An exclusive link publishes a new root AGENTS.md without replacing concurrent
files; cleanup removes the staging link. Existing entries are detected without
following symlinks and remain untouched. Recovery permits that one root path only
for initialization, validates every state before writes, excludes the guide from
canonical membership checks and refuses external changes. Ordinary mutations retain
their direct-node-only path boundary.

Tests cover packaged text/current contracts, fresh and repeated init, invalid bodies,
existing empty/binary/directory/symlink guides, publication races, interruptions,
all-before-any recovery, illegal journal paths and readable/JSON receipts. Isolated
wheel/source installs verify the actual resource and owner-byte preservation;
filesystem and power-loss limits remain explicit rather than hidden fallbacks.

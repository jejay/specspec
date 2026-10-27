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
- path: tests/test_local_state.py
---
# Package and safely concatenate initialization instructions

The distribution contains one static generic guide, loaded through package resources.
Initialization validates a single manifesto and safe root instruction target, checks
Git availability and ensures a Git working tree before publishing node/guide bytes,
reusing a containing repository instead of creating nested Git metadata. Git metadata is not claimed by graph rollback. No staging, commit, identity
configuration or hook management is performed.

The workspace lock and bounded byte journal live inside .specspec/local. An absent
guide is exclusively created; an existing regular file retains its exact byte prefix
and receives the template after a separating paragraph. Changed targets reject
publication and recovery. Initialization recovery permits AGENTS.md originals while
ordinary edit journals remain direct-node-only. Direct nodes and the runtime subtree
have separate inventories. Interrupted initialization can recover partial publication.

Tests cover real Git setup and missing/failing Git, invalid bodies, empty/binary
prefixes, unsafe targets, append/create receipts, concurrent changes, publication
interruptions and all-before-any rollback. Package and installed-host checks exercise
the actual template and initialization flow without owner installation.

The existing exclusion helper protects runtime data during initialization.

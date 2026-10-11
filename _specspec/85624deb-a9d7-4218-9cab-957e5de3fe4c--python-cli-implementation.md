---
id: 85624deb-a9d7-4218-9cab-957e5de3fe4c
type: implementation
parents:
- 6c457b0a-654e-4545-a4b4-667f467be4f3
- 811feda6-a914-4e83-82c5-034e4f337a61
- ca580dc7-c7fa-48bc-91b1-59243144a0bf
- f0d0d18b-b52e-4eef-ab13-da7bedfd07a2
sources:
- path: pyproject.toml
- path: src/specspec/__main__.py
- path: src/specspec/cli.py
  symbol: context
- path: src/specspec/cli.py
  symbol: main
- path: tests/test_api.py
- path: tests/test_core.py
- path: src/specspec/cli.py
  symbol: migrate_command
- path: src/specspec/cli.py
  symbol: withdrawal_command
- path: tests/test_migration.py
  symbol: test_cli_migration_and_withdrawal_filters_have_no_approval_commands
---
# Package the hash-free Python CLI and JSON interface

Hatchling packages src/specspec and exposes specspec.cli:main. Click delegates to
the shared model/graph/workspace/Git backend. JSON API 3 exposes normalized node
records, withdrawal booleans, graph format versions and structured diagnostics,
without managed_hash or fingerprint fields. --expect is removed from every command
and the library; there is no accept command, status filter or approval step.

add/update, explicit withdrawal batches, live/retired listing, complete ancestor
context and byte budgets remain. migrate converts valid v1/v2 files to v3 without
checking obsolete hashes. Body input uses UTF-8 stdin/files. Normal tool writes
reject unmigrated workspaces with guidance, but valid manual edits are readable
and usable before/after migration. CLI export/show/list/context/impact/validation
and staged checks emit no fingerprints.

Tests cover hash-free outputs, removed options, manual changes, legacy conversion,
idempotence, withdrawal, parent-before-child context, UTF-8/CRLF and exact budgets.
No new distribution publication or production correctness claim is made.

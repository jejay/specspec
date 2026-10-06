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
managed_hash: fd67f506f95d85b68e105b5babf9a9bdfa6eab85af0757cb9cb8fda8ac1490f9
---
# Package the approval-free Python CLI and JSON interface

Hatchling packages src/specspec and exposes specspec.cli:main. Click commands call
the shared model, graph, workspace, and Git backend. JSON API version two exposes
retired booleans, graph format versions, fingerprints, and structured diagnostics,
never proposed/accepted node status. There is no accept command or status filter.

add and update save nodes without approval stages. retire and restore are explicit
withdrawal batches; list offers live/retired filters. migrate converts a validated
legacy graph with optimistic concurrency and the normal journal/recovery workflow.
All normal mutation commands reject unmigrated workspaces with actionable guidance.

Context export includes complete ancestors and optional live children/siblings,
using sibling_ids instead of proposal_ids. It deduplicates and measures the actual
serialized response, including API/envelope/omission metadata, against byte budgets.
Retired context remains available explicitly. Binding text uses UTF-8 stdin/file input.

CLI tests exercise conversion, idempotence, removed approval commands/filters,
withdrawal/restoration, sibling context, UTF-8/CRLF, and byte-budget boundaries.
Local isolated pipx/uvx launches were smoke-tested in the preceding implementation;
no new publication or PyPI release is claimed.

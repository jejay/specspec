---
id: 85624deb-a9d7-4218-9cab-957e5de3fe4c
type: implementation
status: proposed
parents:
- f0d0d18b-b52e-4eef-ab13-da7bedfd07a2
- 6c457b0a-654e-4545-a4b4-667f467be4f3
- ff0c8e51-7aaa-4b13-97db-9623dc70d87c
- 811feda6-a914-4e83-82c5-034e4f337a61
sources:
- path: pyproject.toml
- path: src/specspec/cli.py
  symbol: main
- path: src/specspec/cli.py
  symbol: context
- path: src/specspec/__main__.py
- path: tests/test_core.py
- path: tests/test_api.py
managed_hash: bbafd4a4447d2432bbe3a05632a7847e180259036e5c054eb3b75d9dca60b1c8
---
# Package the Python CLI and shared JSON interface

Hatchling packages `src/specspec` and exposes `specspec.cli:main` as the console
entry point. Click commands delegate to the shared model, graph, workspace, and
Git modules rather than duplicating their validation rules. Body input uses UTF-8
stdin/file bytes; JSON output is versioned and machine-readable.

Context export computes complete ancestor requirements and the actual serialized
budget. Explicit batch lifecycle commands validate the resulting graph without
silently approving ancestors. CLI and encoding/budget tests exercise these paths.
Local isolated pipx/uvx launches have been smoke-tested; no PyPI release is claimed.

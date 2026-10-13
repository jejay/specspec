---
id: z3QQuTM=
type: implementation
parents:
- LvYBN_4=
- -9Up2uc=
- apEb_pM=
- WpYvGUo=
sources:
- path: pyproject.toml
- path: src/specspec/__main__.py
- path: src/specspec/cli.py
- path: tests/test_api.py
- path: tests/test_core.py
- path: tests/test_ids.py
---
# Package the shared CLI and complete machine context

Hatchling packages `src/specspec`; Click exposes `specspec.cli:main` through the
console entry point and `python -m specspec`. Commands cover init, validate,
add/update/delete, list/show/context/impact, JSON/Mermaid export, diff, hooks,
recovery, native editor planning and source regions. UTF-8 files/stdin carry bodies.

API 5 emits a single JSON envelope with normalized full-ID records and actionable
structured diagnostics. Mutation output reports changed IDs and affected graph
context. Warned cascade confirmation emits diagnostics before writes. Context
measures the complete serialized envelope, requires the ancestor closure and
explicitly lists optional omissions. Tests exercise output/exit boundaries, exact
budgets, arguments/IDs, manual edits and command guards.

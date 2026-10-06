---
id: beeca399-453b-4b33-8779-29a232c5e5ec
type: implementation
parents:
- 003d697b-4104-4fdf-8e05-0db572c436d0
- 624d0f3c-391d-4575-be87-3001f16052f6
- ca580dc7-c7fa-48bc-91b1-59243144a0bf
sources:
- path: src/specspec/workspace.py
  symbol: initialize
- path: src/specspec/workspace.py
  symbol: mutate
- path: src/specspec/workspace.py
  symbol: recover
- path: tests/test_additional.py
- path: tests/test_recovery.py
- path: tests/test_transactions.py
- path: src/specspec/workspace.py
  symbol: migrate
- path: src/specspec/workspace.py
  symbol: set_retired
- path: tests/test_migration.py
  symbol: test_interrupted_migration_recovers_the_complete_original_schema
managed_hash: 8a6e40753b511a6cc35eec224010fd2e92530e0083484dbf41f42b366f58584c
---
# Apply, migrate, and recover validated workspace edits

initialize creates a format-two graph without approval statuses. mutate requires a
valid current-schema workspace, checks expected fingerprints and original bytes,
and journals replacements under the workspace lock before canonical writes.
set_retired changes withdrawal explicitly; ordinary content edits have no acceptance
transition or parent-review prerequisite.

migrate validates original v1 integrity under the same lock, then converts all nodes
through one recoverable batch. It preserves identities, paths, body bytes, parents,
sources, extensions, and unaffected comments, maps withdrawal, and discards obsolete
approval metadata. Ordinary writes to legacy workspaces require explicit migration;
a repeated v2 migration makes no canonical changes. No read refreshes hashes.

Tests inject interruption into both ordinary batches and migration. recover restores
only known original/replacement bytes, including the complete original schema after
partial conversion, and refuses intervening edits. Verification also covers competing
writers, stale fingerprints, unsafe state, and corrupt input that must not be blessed.
Process-interruption recovery is not a claim of full power-loss durability or immunity
to adversarial filesystem races.

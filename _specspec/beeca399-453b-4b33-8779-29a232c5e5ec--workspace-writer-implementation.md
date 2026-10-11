---
id: beeca399-453b-4b33-8779-29a232c5e5ec
type: implementation
parents:
- 003d697b-4104-4fdf-8e05-0db572c436d0
- 624d0f3c-391d-4575-be87-3001f16052f6
- ca580dc7-c7fa-48bc-91b1-59243144a0bf
sources:
- path: src/specspec/workspace.py
  symbol: mutate, migrate, recover
- path: tests/test_core.py
- path: tests/test_additional.py
- path: tests/test_migration.py
- path: tests/test_markdown.py
---
# Apply, migrate and recover validated edits without content hashes

initialize writes format-three files. mutate locks tool writers, validates current
and candidate graphs, compares original file bytes and journals replacements before
writing. Manual changes are permitted; neither reads nor writes calculate or check
managed_hash/fingerprints. Withdrawal remains explicit, not an approval transition.

migrate accepts structurally valid v1/v2 data even after manual changes, ignores
obsolete markers and converts the complete graph to v3 in one recoverable batch.
Preserve IDs, paths, body bytes, parents, sources, extensions and comments while
removing old hashes/approval fields. Ordinary tool writes require explicit conversion
first; repeated v3 migration is a no-op. Both repository working graphs were migrated
through the CLI rather than hand-editing canonical files.

Tests inject interrupted writes/migration; recover restores only known original or
replacement bytes and refuses intervening edits. Competing tool writers, unsafe
state, schema failures and original-byte races remain checked. Noncooperating editors
can still race an atomic replacement; full power-loss/adversarial race protection is
not claimed. There is no snapshot expectation parameter or stored content marker.

---
id: beeca399-453b-4b33-8779-29a232c5e5ec
type: implementation
status: proposed
parents:
- 624d0f3c-391d-4575-be87-3001f16052f6
- 003d697b-4104-4fdf-8e05-0db572c436d0
sources:
- path: src/specspec/workspace.py
  symbol: initialize
- path: src/specspec/workspace.py
  symbol: mutate
- path: src/specspec/workspace.py
  symbol: recover
- path: tests/test_transactions.py
- path: tests/test_recovery.py
- path: tests/test_additional.py
managed_hash: cc44d823661b0c41131d8536808b4096f95f2ad23612bb5d37ed47e8df788e54
---
# Apply and recover validated workspace edits

`initialize` stages a new manifesto directory before exposing it. `mutate` validates
proposed bytes, checks optimistic concurrency, journals originals/replacements,
and applies canonical writes under a lock outside `_specspec`. `recover` restores
only recognized file states and refuses unrelated intervening edits.

Verification covers a real injected partial-batch failure, competing writers,
external edits, stale fingerprints, orphan staging, and unsafe recovery journals.
Recovery handles process interruption; stronger durability remains unproven.

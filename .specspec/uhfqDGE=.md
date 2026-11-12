---
id: uhfqDGE=
type: implementation
parents:
- 6SyZ-BU=
sources:
- path: src/specspec/workspace.py
- path: tests/test_additional.py
- path: tests/test_core.py
- path: tests/test_first_use_messages.py
- path: tests/test_ids.py
- path: tests/test_markdown.py
---
# Apply and recover validated byte-checked workspace transactions

`initialize` exposes a staged valid directory from supplied manifesto text.
`mutate` locks, loads/validates saved files, builds and validates the candidate, rejects parent IDs that a changed node introduces and that name no node or node file of the candidate (require_known_parents),
journals original/replacement states, byte-checks targets and applies replacements.
Null states physically delete files. `add_node` generates collision-checked IDs
inside the lock; `update_node` preserves identity with explicit field changes.
`delete_nodes` executes the reviewed exact selected-file plan. Initialization also places the packaged root guide through place_guide; its separate
initialization explanation supplies ownership and recovery details.

`recover` restores only known original/replacement/absence states, retaining
intervening external text for user resolution. The lock holder checks again for a journal or stage files after acquiring the lock. Writers retry the exclusive lock for LOCK_WAIT_SECONDS (3 s), reads wait as long in runtime_diagnostics, and a lock that remains is reported with LOCKED_MESSAGE; only a journal without a lock is an interrupted edit. Staged files and the journal are written with write_durably (fsync), and the journal rename is followed by a directory sync where the platform has one, so recover removes a journal that does not parse, together with its staged files, and reports that no node changed. Tests exercise competing writers, unsafe state, byte races, interruptions,
canonical deletion and recovery. Its
scope is cooperating/process-interruption safety with explicit filesystem limits.

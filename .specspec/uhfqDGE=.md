---
id: uhfqDGE=
type: implementation
parents:
- 6SyZ-BU=
sources:
- path: src/specspec/workspace.py
- path: tests/test_additional.py
- path: tests/test_core.py
- path: tests/test_ids.py
- path: tests/test_markdown.py
---
# Apply and recover validated byte-checked workspace transactions

`initialize` exposes a staged valid directory from supplied manifesto text.
`mutate` locks, loads/validates saved files, builds and validates the candidate,
journals original/replacement states, byte-checks targets and applies replacements.
Null states physically delete files. `add_node` generates collision-checked IDs
inside the lock; `update_node` preserves identity with explicit field changes.
`delete_nodes` executes the reviewed exact selected-file plan. Initialization
additionally publishes a packaged root guide only when absent; its separate
initialization explanation supplies ownership and recovery details.

`recover` restores only known original/replacement/absence states, retaining
intervening external text for user resolution. Tests exercise competing writers,
unsafe state, byte races, interruptions, canonical deletion and recovery. Its
scope is cooperating/process-interruption safety with explicit filesystem limits.

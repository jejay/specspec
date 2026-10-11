---
id: uhfqDGE=
type: implementation
parents:
- ME4UXTA=
- 6SyZ-BU=
- apEb_pM=
sources:
- path: src/specspec/workspace.py
  symbol: new_node, initialize, mutate, add_node, recover
- path: tests/test_core.py
- path: tests/test_additional.py
- path: tests/test_ids.py
  symbol: canonical IDs, current-only validation and collision retry
- path: tests/test_markdown.py
---
## Current compact-ID and history correction

The implementation/verification below records earlier revisions. Its legacy-reader,
schema-migration, original API-2 receipt and root-history compatibility descriptions
are superseded by qowy5AI= and YaXJpGE=. Current production code supports only the
canonical Base64url node scheme, with no old-schema reader or migration command.
The default node-editor association is **/_specspec/???????=*.md. Gantt's maintained
history is rewritten and bundled; tests do not require old root graph revisions.
Earlier run counts are historical evidence, not claims about this revision. The
separate current implementation record documents the new checks and limitations.

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

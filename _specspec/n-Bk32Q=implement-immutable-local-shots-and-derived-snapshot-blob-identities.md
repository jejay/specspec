---
id: n-Bk32Q=
type: implementation
parents:
- P2i_png=
- 63jO49Q=
- rQTg56g=
sources:
- path: docs/spotlights.md
- path: docs/cli.md
- path: src/specspec/annotation_commands.py
- path: src/specspec/annotations.py
- path: src/specspec/application.py
- path: src/specspec/cli.py
- path: src/specspec/editor.py
- path: tests/test_annotations.py
- path: tests/test_cli_compact.py
---
# Implement immutable local shots and derived snapshot blob identities

The spotlight backend validates a whole ordered group payload, captures full node
IDs and exact SHA-1/SHA-256 Git-format addresses, retains original bytes locally and
publishes one atomic shot file under the cooperating workspace writer lock. Named
six-color inks and explicit hex colors remain independent of semantic graph fills.
The local store has explicit count/byte budgets, protected malformed-data errors,
Git-local exclusion and tracked-state refusal. Flush checks a host-reviewed shot-ID
set and removes only spotlight shot/content files. Canonical node format stays 5;
the spotlight store has its own local format.

Public spotlight add/show/flush commands expose direct color/ID/message capture
from saved workspace or an explicit immutable revision, plus derived workspace/
HEAD/requested-tree presence. Add parses a color/ID prefix, uses purple by default,
rejects empty sets and duplicate members, and repeats one message across internal
color groups. Known names and full canonical IDs delimit that prefix, including
dash-leading IDs. Internal retained-byte reads remain independent of graph validity.
Graph reads and native plans expose target/base raw-byte blob identities as derived
application metadata, preserving native Save, canonical fields and transaction guards.

Focused backend tests cover joint rejection/publication, literal bytes and native
overlays, retained workspace-only versions without Git object creation, SHA-256,
local Git exclusion, corruption, budgets and reviewed-flush races. Temporal tests
exercise renames, changed commits and branch switching in an independent clone of
the maintained current-schema Gantt history. These are bounded local persistence
and membership checks, not semantic answer validation or exhaustive history indexing.

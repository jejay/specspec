---
id: 63jO49Q=
type: requirement
parents:
- P2i_png=
- Yfy0414=
---
# Resolve spotlight references against exact snapshot bytes

Retain exact captured node bytes locally under their full SHA-1 or SHA-256 Git blob
address, including workspace versions whose bytes have not entered Git's object
database. Literal node-file bytes, including comments and line endings, determine
identity; Git clean filters and line-ending normalization retain their own roles. Local copies preserve the evidence through Git garbage collection and
history rewriting. Content addresses are local spotlight references and derived
read metadata; canonical node format and edit protection keep their own contracts.

Resolve members by both full node ID and exact bytes, independent of filename-only
renames. Capture provenance records an immutable commit ID where applicable.
Workspace captures identify saved files and their HEAD context without representing
uncommitted content as committed. Application snapshots supply derived blob
addresses for their actual saved/native-overlay target and comparison base.

Check presence in the displayed target/base or an explicitly requested CLI revision.
Report exact, changed, absent or unavailable resolution rather than retargeting a
shot. Git blob identity has no intrinsic commit ancestry; matching commit membership
is derived from inspected trees, not an eagerly persisted list of all history.
Captured-text preview remains available independently of present graph validity.

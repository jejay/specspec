---
id: Yfy0414=
type: requirement
parents:
- SRsw2W0=
- tvic3PQ=
- LvYBN_4=
---
# Validate index blobs and compare graph snapshots by ID

Validate exactly the staged Git blobs, not their working-file counterparts, before
committing. Preserve existing hooks and respect Git's configured hook directory.
Read index and historical snapshots without checking out another revision.

Compare nodes by ID and report semantic changes separately from filename-only
renames. Return added/removed edges and base/target records. Review impact uses
both graphs so removed relationships cannot hide affected descendants; linked
source changes identify implementation records and their requirement ancestors.

Origin: [CONCLUSION_SPEC.md](../CONCLUSION_SPEC.md), Git hook and revision diffs.

## Current source-address refinement

jsIUeP0=/VnSF9BE= supersede format/API 3 with current-only format/API 4.
Structured Git blob IDs are source snapshot addresses, not restored managed_hash,
fingerprints, edit-provenance or approval gates. Optional hook check --sources
checks exact-index source regions and object retention without writes/staging.
Default graph hook, watcher/native persistence and byte transactions stay in scope.

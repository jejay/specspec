---
id: Yfy0414=
type: requirement
parents:
- SRsw2W0=
- tvic3PQ=
- LvYBN_4=
---
## Current deletion correction

xu6W0c4=/5d5oDCM= supersede stored withdrawal, retired flags/controls and
format/API four with current-only format/API five. Withdraw by deleting the
Markdown file, keep reasons/earlier explanations in Git, and show HEAD-relative
deleted ghosts in the default workspace until commit. All earlier version/flag
workflow descriptions below are historical, not the current contract. Source
blob anchoring, no approval gates, native persistence distinctions and current-only
example-history policy remain; all retained Gantt revisions use actual deletions.

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

---
id: lnjP2Qk=
type: requirement
parents:
- ME4UXTA=
- kpatAr8=
- apEb_pM=
retired: true
---
# Detect unmanaged semantic changes with content hashes

Maintain a `managed_hash` over canonical semantic metadata and binding Markdown.
Exclude filenames and the hash itself, sort non-semantic parent/source order,
and normalize line endings only. Validation reports mismatches without blessing
manual changes by refreshing the hashes.

The marker detects ordinary unmanaged edits; it does not authenticate a reviewer
or prevent a user from forging a digest or bypassing local checks.

Origin: [CONCLUSION_SPEC.md](../CONCLUSION_SPEC.md), managed edits and integrity.

## Withdrawal

The user explicitly removed content-marker and fingerprint enforcement, permitting
manual Markdown edits. The hash-free-schema-and-watcher-reconciliation conclusion
replaces this choice; historical reasoning is retained, not an active restriction.

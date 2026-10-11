---
id: 9e4eeace-d288-49bb-8365-6af0372daf5c
type: requirement
parents:
- 003d697b-4104-4fdf-8e05-0db572c436d0
- aee203cc-e68a-4b0d-af18-9920e5303e49
- ca580dc7-c7fa-48bc-91b1-59243144a0bf
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

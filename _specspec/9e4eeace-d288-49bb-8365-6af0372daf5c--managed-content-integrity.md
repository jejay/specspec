---
id: 9e4eeace-d288-49bb-8365-6af0372daf5c
type: requirement
status: proposed
parents:
- 003d697b-4104-4fdf-8e05-0db572c436d0
- aee203cc-e68a-4b0d-af18-9920e5303e49
- d51d6da3-4142-4fc7-b593-d935ee5fdf6f
managed_hash: f3c450c1837a984f25128a059fe630e5e32f3831dfe19d69d1754aeac188c3fb
---
# Detect unmanaged semantic changes with content hashes

Maintain a `managed_hash` over canonical semantic metadata and binding Markdown.
Exclude filenames and the hash itself, sort non-semantic parent/source order,
and normalize line endings only. Validation reports mismatches without blessing
manual changes by refreshing the hashes.

The marker detects ordinary unmanaged edits; it does not authenticate a reviewer
or prevent a user from forging a digest or bypassing local checks.

Origin: [CONCLUSION_SPEC.md](../CONCLUSION_SPEC.md), managed edits and integrity.

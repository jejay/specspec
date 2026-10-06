---
id: 624d0f3c-391d-4575-be87-3001f16052f6
type: requirement
parents:
- 003d697b-4104-4fdf-8e05-0db572c436d0
- 9e4eeace-d288-49bb-8365-6af0372daf5c
managed_hash: 75ec9511293d96e5650b9f75b72ec8056b6da4e1bcc00b7b4ae2e08077968315
---
# Validate and journal managed graph mutations

Validate the current and candidate snapshots under a workspace lock. Support an
expected semantic fingerprint and compare original file bytes before replacement.
Stage replacements and record recoverable original/replacement states outside
`_specspec`, in the ignored `.specspec-local` directory.

Interrupted batches block further edits until recovery. Recovery must not overwrite
intervening external edits. Process-interruption recovery is not a claim of full
power-loss durability or adversarial filesystem race protection.

Origin: [CONCLUSION_SPEC.md](../CONCLUSION_SPEC.md), transaction strategy.

---
id: 624d0f3c-391d-4575-be87-3001f16052f6
type: requirement
status: proposed
parents:
- 003d697b-4104-4fdf-8e05-0db572c436d0
- 9e4eeace-d288-49bb-8365-6af0372daf5c
managed_hash: 93053456ff1e381441c8f44d29ff994343afe3a94bb7617661d060aef4189cf3
---
# Validate and journal managed graph mutations

Validate the current and proposed snapshots under a workspace lock. Support an
expected semantic fingerprint and compare original file bytes before replacement.
Stage replacements and record recoverable original/replacement states outside
`_specspec`, in the ignored `.specspec-local` directory.

Interrupted batches block further edits until recovery. Recovery must not overwrite
intervening external edits. Process-interruption recovery is not a claim of full
power-loss durability or adversarial filesystem race protection.

Origin: [CONCLUSION_SPEC.md](../CONCLUSION_SPEC.md), transaction strategy.

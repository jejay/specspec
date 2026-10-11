---
id: 624d0f3c-391d-4575-be87-3001f16052f6
type: requirement
parents:
- 003d697b-4104-4fdf-8e05-0db572c436d0
- 93224022-0c11-4260-b09e-2925b7aacf0f
---
# Validate and journal tool-driven graph mutations

Validate current and candidate snapshots under a workspace lock. Compare original
file bytes before replacement, without fingerprints or stored content markers.
Stage replacements and journal original/replacement states outside _specspec in
the ignored .specspec-local directory. Manual edits are allowed, not recommended.

Interrupted batches block further tool writes until recovery. Recovery must not
overwrite intervening external edits. Process-interruption recovery is not a claim
of full power-loss durability or adversarial filesystem race protection.

Origin: CONCLUSION_SPEC.md transaction strategy, revised by the user's hash-removal
request. Byte checks protect a transaction, not the provenance of a prior edit.

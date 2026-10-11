---
id: 6SyZ-BU=
type: requirement
parents:
- ME4UXTA=
- tvic3PQ=
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

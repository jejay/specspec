---
id: uZYoQ_w=
type: requirement
parents:
- rMoZbeg=
- -9Up2uc=
retired: true
---
# Explore persistent review-context receipts

Explore recording the recursive parent fingerprints against which a conclusion
was reviewed, so ancestor edits can expose stale review context independently of
ordinary Git diffs. Define canonicalization, migration, and reviewer-identity
limitations before adopting a receipt schema.

This candidate is not implemented. The current review boundary is the actual
specification/code diff and explicit human review; content hashes do not prove
approval. Do not add receipt sidecars to `_specspec`.

Origin: [CONCLUSION_SPEC.md](../CONCLUSION_SPEC.md), deferred review receipts.

## Withdrawal

A persistent per-node approval-receipt workflow is not part of the current risk-proportionate review direction. It was never implemented.
History is retained; see the risk-proportionate-review intention and its separate schema conclusion.

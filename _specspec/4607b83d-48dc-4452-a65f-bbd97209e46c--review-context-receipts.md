---
id: 4607b83d-48dc-4452-a65f-bbd97209e46c
type: requirement
parents:
- ff0c8e51-7aaa-4b13-97db-9623dc70d87c
- 811feda6-a914-4e83-82c5-034e4f337a61
managed_hash: 8ba79f0a1e5cc4dca20b3d8d363955bd0e61467ff479ef625e3cb29c377f76a3
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

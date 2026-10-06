---
id: 4607b83d-48dc-4452-a65f-bbd97209e46c
type: requirement
status: proposed
parents:
- ff0c8e51-7aaa-4b13-97db-9623dc70d87c
- 811feda6-a914-4e83-82c5-034e4f337a61
managed_hash: 3227d79d9d478bf324ac33dc2371c0cfc4d4a78c6d4ab0493aa94ef7fbede980
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

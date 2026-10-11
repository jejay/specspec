---
id: 8319ae0f-ba84-4748-a119-e77865dbff34
type: requirement
parents:
- e45b1bef-bcd9-4c8e-a48e-8f048f063e58
- afe92d9e-343f-4d90-8405-81eeaf4cfbeb
- fb8e2355-d6b0-44eb-a011-3378d012e66d
---
# Rebuild a portable independent Git history for the Gantt test project

The existing Gantt stages were committed inside the surrounding SpecSpec repository.
Rebuild their ordered independent project trees into a standalone Git fixture,
using current compact IDs, hash-free metadata and actual current CLI receipts.
Store its complete history as a checked-in Git bundle plus a revision ledger.
Tests clone the bundle into disposable repositories, not a silently installed
nested .git directory or an attempt to parse SpecSpec's obsolete parent revisions.
Unrelated surrounding development commits are not rewritten or force-pushed.

Use one random old/new mapping throughout every Gantt snapshot. Rebuild all three
spec/code pairs and a final audit, retain meaningful app code/story/withdrawal
semantics, and mark reconstruction honestly rather than passing transformed old
API-2 receipts off as current executions. Generate new receipts by replaying the
recorded operations through the current CLI in a fresh graph, mapping references
to the actual new IDs. Remove fingerprint/expect bookkeeping, legacy format tests
and original-history compatibility requirements. Application JSON version-one
conversion is an app feature, not an obsolete SpecSpec schema, and remains tested.

Verify every maintained commit's schema/DAG, exact staged index, full IDs, ancestor
context, semantic/edge/source diffs, spec-before-code ordering, both major withdrawal
sets and runnable application stages. Compare the rebuilt final graph with the
working example. Document clone/diff/worktree commands against this history. The
self-referencing root still receives present-working-graph/source validation, but
old root revisions are not a versioning compatibility test corpus.

Origin: revisable scope/fixture choice for the user's requested compliant Gantt
history. Git object IDs identify fixture commits, not an added node hash scheme.

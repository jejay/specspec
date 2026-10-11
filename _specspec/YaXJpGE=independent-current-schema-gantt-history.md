---
id: YaXJpGE=
type: requirement
parents:
- Oou-SvU=
- YWl-8jE=
- Yfy0414=
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

---
id: fb8e2355-d6b0-44eb-a011-3378d012e66d
type: requirement
parents:
- 51c3e963-674e-4d5d-bd7a-b8d63649e1c8
- 93224022-0c11-4260-b09e-2925b7aacf0f
- 6c457b0a-654e-4545-a4b4-667f467be4f3
---
# Validate index blobs and compare graph snapshots by ID

Validate exactly the staged Git blobs, not their working-file counterparts, before
committing. Preserve existing hooks and respect Git's configured hook directory.
Read index and historical snapshots without checking out another revision.

Compare nodes by ID and report semantic changes separately from filename-only
renames. Return added/removed edges and base/target records. Review impact uses
both graphs so removed relationships cannot hide affected descendants; linked
source changes identify implementation records and their requirement ancestors.

Origin: [CONCLUSION_SPEC.md](../CONCLUSION_SPEC.md), Git hook and revision diffs.

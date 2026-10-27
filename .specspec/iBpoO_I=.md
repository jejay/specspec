---
id: iBpoO_I=
type: requirement
parents:
- YaXJpGE=
---
# Compare tracked fixture snapshots through their existing Git clean policy

A maintained fixture's saved runtime/test files agree with its bundled Git contents
under the owning checkout's established Git clean policy. Prefer byte equality;
when checkout filters or newline encoding differ, compare Git's filtered saved-file
object address with the exact expected blob bytes using that repository's object
format. Preserve SHA-1 and SHA-256 behavior. Meaningful text, trailing blank lines
and EOF changes remain differences unless the owner's existing Git policy permits
them. Verification changes neither source bytes, Git config/attributes nor index.
Raw Git objects, source-region evidence and transaction guards remain byte-exact.

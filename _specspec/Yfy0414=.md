---
id: Yfy0414=
type: requirement
parents:
- tvic3PQ=
---
# Validate exact index blobs and compare revision graphs by ID

Check exactly the staged node blobs, including partially staged files, using
NUL-delimited Git paths and object reads. Conflicted stages, unsafe entries,
unsupported schema and invalid graphs produce diagnostics. Owner-configured hooks/CI call check --staged. Hook files and chaining remain
under ordinary Git tooling and preserve existing hook policy.

Read worktree, index and historical snapshots with their current schema. Compare
full IDs to return added/removed nodes, semantic body/parent/metadata changes,
base/target records and changed edges. Compute potential
impact from both ancestor/descendant contexts so removed links remain represented.
Source-file changes reach linked implementation nodes and their requirement ancestors
using references in both snapshots, with conservative file-level impact.

Absent base specifications and genuinely unborn HEAD have explicit empty baselines.
Invalid revisions report incomplete comparison/impact with actionable diagnostics.
Git reads leave checkout, staging, branches and refs under the user's control.
Optional `check --staged --sources` assesses staged source mapping and retention.

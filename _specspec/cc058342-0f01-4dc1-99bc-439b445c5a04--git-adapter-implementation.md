---
id: cc058342-0f01-4dc1-99bc-439b445c5a04
type: implementation
parents:
- 51c3e963-674e-4d5d-bd7a-b8d63649e1c8
- 93224022-0c11-4260-b09e-2925b7aacf0f
- ca580dc7-c7fa-48bc-91b1-59243144a0bf
- fb8e2355-d6b0-44eb-a011-3378d012e66d
sources:
- path: src/specspec/git.py
  symbol: git_snapshot, semantic_diff, source_change_impact, install_hook
- path: tests/test_git.py
- path: tests/test_additional.py
- path: tests/test_migration.py
  symbol: test_staged_and_historical_v1_v3_snapshots_remain_readable
- path: tests/test_markdown.py
---
# Load staged and historical graph snapshots without provenance enforcement

git_snapshot reads exact index/commit node blobs with NUL-delimited Git output,
without a shell or checkout. Each snapshot selects its own v1/v2/v3 manifesto
version. Obsolete legacy hash fields are ignored, not exposed or checked. Manual
body/metadata changes are valid when their actual schema/graph is consistent.

semantic_diff compares normalized node contents by ID, withdrawal, paths and
old/new edges. file_changes compares raw bytes directly, not byte hashes. Legacy
approval labels aren't invented review stages. Migration changes only the root
version semantically; raw frontmatter removals remain visible. Linked source impact
uses both revisions and is informational review context, not approval evidence.

Disposable tests stage schema corruption masked by a repaired worktree, and allow
valid manual edits including legacy blobs. Partial staging, empty baselines,
renames/edges, source impact and v1/v2-to-v3 history remain covered. Hooks are opt-in,
preserve existing/custom hooks, and check the exact index. No staging/committing,
branch switching, or historical blob rewriting is introduced.

---
id: cc058342-0f01-4dc1-99bc-439b445c5a04
type: implementation
parents:
- 51c3e963-674e-4d5d-bd7a-b8d63649e1c8
- 9e4eeace-d288-49bb-8365-6af0372daf5c
- ca580dc7-c7fa-48bc-91b1-59243144a0bf
- fb8e2355-d6b0-44eb-a011-3378d012e66d
sources:
- path: src/specspec/git.py
  symbol: git_snapshot
- path: src/specspec/git.py
  symbol: install_hook
- path: src/specspec/git.py
  symbol: semantic_diff
- path: src/specspec/git.py
  symbol: source_change_impact
- path: tests/test_additional.py
- path: tests/test_git.py
- path: tests/test_migration.py
  symbol: test_staged_and_historical_v1_v2_snapshots_remain_readable
managed_hash: 3465dfd09dcd6d3cb22b74937e62e6e96615013c07877eb0e1fa45b91567f05f
---
# Load staged and historical graph snapshots across schema versions

git_snapshot reads regular node blobs from the index or a resolved commit using
NUL-delimited Git output and no shell. Each revision selects its own manifesto
version. Original v1 hashes remain verified while normalized node records expose
no approval status; v2 uses withdrawal booleans. No checkout or historical rewrite
is needed for cross-version comparison.

semantic_diff compares identities, binding metadata, withdrawal, old/new edges,
and paths. Obsolete v1 accepted/proposed differences are not invented current
review stages. A pure migration retains all IDs/links and changes the root version
semantically; raw file_changes still exposes the converted frontmatter. Source
impact maps changed linked files to implementation records and ancestors in both
snapshots; added/changed/source badges are not approval or correctness claims.

Disposable repository tests cover partial staging, corrupt staged blobs masked
by repaired worktrees, empty baselines, renames, removed edges, source impact,
and v1-to-v2 index/commit snapshots. Hook installation remains opt-in, exclusively
creates its file, and preserves existing/custom hooks. CLI/editor Git operations
do not automatically stage, commit, or switch branches.

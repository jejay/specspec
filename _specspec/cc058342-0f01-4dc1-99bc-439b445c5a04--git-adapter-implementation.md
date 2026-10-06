---
id: cc058342-0f01-4dc1-99bc-439b445c5a04
type: implementation
status: proposed
parents:
- 51c3e963-674e-4d5d-bd7a-b8d63649e1c8
- fb8e2355-d6b0-44eb-a011-3378d012e66d
- 9e4eeace-d288-49bb-8365-6af0372daf5c
sources:
- path: src/specspec/git.py
  symbol: git_snapshot
- path: src/specspec/git.py
  symbol: semantic_diff
- path: src/specspec/git.py
  symbol: source_change_impact
- path: src/specspec/git.py
  symbol: install_hook
- path: tests/test_git.py
- path: tests/test_additional.py
managed_hash: 9f832cf939324651c31dfe51fa4afad56139991088c54653413fbc2ab2e39c17
---
# Load staged and historical graph snapshots

`git_snapshot` reads regular node blobs from the index or a resolved commit using
NUL-delimited Git output and no shell. `semantic_diff` compares identities and old/
new edges; `source_change_impact` maps changed linked code back to implementation
records and ancestors. `install_hook` exclusively creates a pre-commit script and
preserves existing hooks, including custom hook directories.

Tests use disposable repositories to check partial staging, corrupt staged blobs
masked by repaired worktrees, installed-hook execution, empty baselines, renames,
removed edges, nested projects, and source-file impact. The local hook remains
opt-in; these operations never stage files or create commits for the user.

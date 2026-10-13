---
id: 9oE6Ia4=
type: implementation
parents:
- SRsw2W0=
- tvic3PQ=
- apEb_pM=
- Yfy0414=
sources:
- path: src/specspec/git.py
- path: tests/test_additional.py
- path: tests/test_git.py
- path: tests/test_ids.py
- path: tests/test_markdown.py
---
# Read exact Git snapshots and derive semantic/source impact

`git_snapshot` reads NUL-delimited exact index/commit entries and their object bytes
without changing checkout. `unborn_head` distinguishes a genuine empty HEAD baseline
from unavailable revisions. `semantic_diff` compares full IDs, body/parent/metadata
records, file paths and edges, deriving old/new potential impact. Source impact
uses both snapshots' file references and requirement ancestry.

`install_hook` is opt-in, respects Git's hook path and preserves existing hooks.
Disposable current-schema and maintained Gantt tests cover partial staging,
corruption masked by repaired worktrees, renames/edges, sources, baselines and hooks.

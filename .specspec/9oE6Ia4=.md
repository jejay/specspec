---
id: 9oE6Ia4=
type: implementation
parents:
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
records and edges, deriving old/new potential impact. Source impact
uses both snapshots' file references and requirement ancestry.

Owner-managed hooks/CI invoke check --staged against exact index bytes.
Hook files, existing commands and environment selection remain owner-controlled.
Disposable current-schema and maintained Gantt tests cover partial staging,
corruption masked by repaired worktrees, canonical path rejection, edges, sources,
baselines and hooks.

Canonical object reads use bounded metadata/content batches with verified blob bytes.
Derived baseline hints retain fresh ref/tree/object checks and exact index semantics.

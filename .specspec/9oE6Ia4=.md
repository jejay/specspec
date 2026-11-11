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
# Read exact snapshots from Git and derive what changed and which nodes that may affect

`src/specspec/git.py` reads and compares the snapshots. `git_snapshot` lists the entries of the index or of a commit with NUL-delimited paths, reads their blobs and leaves the checkout as it is. `unborn_head` tells a HEAD that has no commit yet, which gives an empty baseline, from a revision that is unavailable. `semantic_diff` matches nodes by full ID. It returns the added, removed and changed nodes with the fields that differ in text, parents and metadata, the records of both sides, the added and removed links and the nodes that may be affected in the base and in the target. `source_change_impact` takes the file links of both snapshots, finds the files among them that changed and returns the implementations that link those files together with their ancestors.

The blobs are read in batches of limited size, first their metadata and then their content, and the bytes of every blob are verified against its ID. Bytes that an editor hands back as a hint for the base of a comparison are used only after the ref, the tree and the object were checked anew, and a read of the index reads the exact staged bytes.

Hooks and CI that an owner has set up call `check --staged`, which reads the exact bytes of the index. The hook files, the commands that a hook already runs and the choice of the environment are the owner's.

`tests/test_git.py`, `tests/test_additional.py`, `tests/test_ids.py` and `tests/test_markdown.py` work on throwaway repositories in the current node format. They cover partial staging, a corrupt staged file behind a repaired working file, the rejection of a path that is no node path, added and removed links, the impact of changed and of new untracked source files, empty baselines and a hook that calls the check. `tests/test_gantt_git.py` repeats the checks of staging, links and source impact on the maintained Gantt history.

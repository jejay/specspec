---
id: i6Y3Z7I=
type: implementation
parents:
- LvYBN_4=
- pA2ls_g=
sources:
- path: src/specspec/graph.py
- path: tests/test_core.py
- path: tests/test_shortcut_freedom.py
- path: docs/graph-structure.md
---
# Index and validate the shortcut-free rooted DAG iteratively

The shared build_graph authority validates parent references/types, root reachability,
terminal implementation grammar and shortcut freedom. Deterministic heap-based Kahn
ordering and iterative traversals support deep/shared graphs. Shortcut checks run
only after the basic graph is sound and provide deterministic alternative-path
witnesses rather than changing canonical edges.

Each invocation derives its graph from actual supplied files. Managed operations
reject invalid complete candidates before writes; reads and native plans diagnose
repairable text. Exact-index checks use staged blobs independently of working files.
Base checks retain their linear traversal and O(V log V) ordering cost; shortcut
checks additionally traverse relevant ancestor subgraphs and produce witness paths.
Verification covers valid unequal-depth multiparent DAGs, long chains, deep shortcuts,
cycles/missing references, remote redundancy introduced by an edit, unchanged bytes
on failed writes, native repair and exact-index/history distinctions.

Current verification passes 268 Python, 167 shared UI, 42 VS Code adapter and nine
Electron unit tests. The closure oracle checks generated arbitrary DAGs and reduced
reachability equivalence. Both current graphs and every retained Gantt revision
are shortcut-free; all 123 actual receipt states and three model stages verify.
Installed format-six graph/paint checks run in both Windows hosts, while complete
window regression remains unconfirmed at later cascade/source-preview assertions;
docs/graph-structure.md records the bounded evidence.

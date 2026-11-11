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
---
# Build and validate the graph in one shared function with iterative walks

`build_graph` in `src/specspec/graph.py` is the one validator that every tool uses. It checks that the graph has exactly one manifesto, that every parent reference resolves and has a permitted type, that an implementation is a leaf under requirements, that the graph has no cycle and that every node is reachable from the manifesto, and it checks shortcut freedom. It orders the nodes with Kahn's algorithm on a heap, which gives the same order on every run, and all its walks are iterative, so that deep graphs and graphs with many shared nodes are handled. The shortcut check runs only when the graph has passed the other checks. For every redundant parent it reports an alternative path, the same on every run, and it leaves the links exactly as they are written.

Every invocation builds its graph from the files that it is given. With `--require-valid` the writer rejects an invalid candidate as a whole before anything is written, and reads and edit plans for editor documents diagnose text that can be repaired. A check of the exact index uses the staged blobs, whatever the working files hold. The basic checks walk the graph in linear time and order it in O(V log V). The shortcut check walks, in addition, the ancestors of every node with several parents and builds the witness paths.

`tests/test_core.py` and `tests/test_shortcut_freedom.py` cover valid graphs whose nodes have several parents at unequal depths, long chains, deep shortcuts, cycles and missing references, a redundancy that an edit introduces at another node, files that keep their bytes when a write is rejected, repair in an editor document and the difference between the exact index and a committed revision. An independent oracle that uses the transitive closure checks generated graphs: the reported shortcuts are exactly the expected ones, and removing them leaves every node with the same ancestors. The verification of the maintained Gantt history checks every revision, the state after each recorded command, every source anchor and every runnable stage of the model.

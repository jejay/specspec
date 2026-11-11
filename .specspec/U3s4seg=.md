---
id: U3s4seg=
type: implementation
parents:
- L5Xamn4=
- 0piRXe0=
- qSK7qA0=
sources:
- path: src/specspec/workspace.py
- path: src/specspec/graph.py
- path: src/specspec/inspection.py
- path: src/specspec/batch.py
- path: src/specspec/cli.py
- path: src/specspec/query.py
- path: src/specspec/query_select.py
- path: src/specspec/git.py
- path: src/specspec/application.py
- path: src/specspec/editor.py
- path: src/specspec/deletion.py
- path: src/specspec/annotations.py
- path: graph-ui-common/host/reads.cjs
- path: graph-ui-common/host/session.cjs
- path: graph-ui-common/media/graph-model.js
- path: graph-ui-common/media/graph.js
- path: tests/test_invalid_workflow.py
- path: tests/test_editor.py
---
# Read, edit and repair an invalid graph through the shared backend and both editors

`workspace.py` and `graph.py` keep, for every snapshot, the inventory of the files, the parsed node records, the declared references, the resolved links and structured diagnostics. `inspection.py` computes the scope of broken references, one finite cause path for each cause and node, and the earlier and the current reading of a node. `query`, `diff` and `check` in `cli.py`, `query.py` and `query_select.py` and the reads of the application protocol in `application.py` use these findings, and each of them starts from the graph as it is, valid or invalid. The writer in `workspace.py` and the planner of combined edits in `batch.py` write in journaled transactions that are safe byte for byte and validate the complete candidate on request. `deletion.py` plans the deletion of exactly the named files and reports the references that it leaves unresolved. Recovery restores the original files also when they formed an invalid graph.

The shared reads, the session, the model and the forms of the graph editors, in `reads.cjs`, `session.cjs`, `graph-model.js` and `graph.js`, speak the application protocol, show the endpoints that are actually broken and diagnose an invalid working graph while the form of a single safe node stays editable. `editor.py` returns the fields of a repair form apart from the nodes of the graph. The header of a manifesto in the current format gives the format version also when its body is invalid, and an edit of an editor document with an empty body or half-typed source JSON works on the fields laid over the file. A `diff` with context reads one snapshot for its context and for its patches. A metric check that starts at a root leaves aside the cycles outside the nodes it was asked for. Outside a Git repository a report with context keeps what the current files show and is marked incomplete. The drift check of a spotlight in `annotations.py` reads the bytes at the node paths, and an unreadable file counts as a present file.

`tests/test_invalid_workflow.py` and `tests/test_editor.py` cover the deletion of a node that is the only parent, a shared parent or deep in the graph; cyclic, disconnected and unreadable input; completeness and metrics; explicit steps of repair; combined edits; consent to deletion; races and recovery; the limits of the protocol; and, independently of the validity of the graph, the rejection of arbitrary paths and of other format versions. The editing in the installed editors is covered by the suites that run in them. The independent Gantt history is rebuilt with receipts of the current tools, and every ref kept in it is checked.

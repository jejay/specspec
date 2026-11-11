---
id: OfBdhms=
type: implementation
parents:
- 79zOr-w=
- ezHjLDs=
sources:
- path: src/specspec/model.py
- path: src/specspec/format.py
- path: src/specspec/workspace.py
- path: src/specspec/cli.py
- path: src/specspec/query.py
- path: src/specspec/output.py
- path: src/specspec/git.py
- path: src/specspec/annotation_commands.py
- path: graph-ui-common/view.cjs
- path: graph-ui-common/media/graph.js
- path: graph-ui-common/media/graph-model.js
- path: graph-ui-common/host/session.cjs
- path: vscode/package.json
- path: tests/test_ids.py
- path: tests/test_core.py
- path: tests/test_editor.py
- path: tests/test_git.py
- path: tests/test_gantt_git.py
- path: tests/test_query.py
- path: tests/test_cli_compact.py
- path: tests/test_repository_docs.py
- path: graph-ui-common/test/graph.test.cjs
- path: graph-ui-common/test/session.test.cjs
- path: vscode/test/extension.test.cjs
- path: example/gantt/history/verify.py
- path: example/gantt/history/cli.jsonl
- path: example/gantt/history/revisions.json
- path: example/gantt/history/gantt.bundle
- path: README.md
- path: tests/test_directory.py
---
# Name node files by ID alone in the backend, the editors and the example history

`model.py` sets the current version of the node format and `API_VERSION`, both 7. `format.py` requires that a file name equals `<id>.md` exactly, inside the one `.specspec` directory. `workspace.py` finds the project by the nearest `.specspec` entry, reads the Markdown files directly in it and leaves out `.specspec/local`. It builds the path of a new node from the ID inside the writer's lock, collision check and transaction, whatever the body says. `init`, `add` and the library take the fields of a node directly. Labels for human readers come from the Markdown headings. `query.py` prints full IDs in the complete parent list of every record. `git.py` reads the node files from the index or from a commit and leaves out `.specspec/local` there as well. It classifies the changes between two snapshots as added, changed in meaning or removed. The tracking of renamed source files is a separate ability of source resolution.

The creation form that both graph editors share, its stored drafts and the checked messages to the host carry the body, the type, the parents and the sources of a node. The custom editor of VS Code finds files that match `???????=.md`, and Python validates their actual metadata and the spelling of their names. Both editors require the same version of the node format. A save of a VS Code text document and a write through specspec's writer are separate paths.

This repository's own graph and the tracked snapshot of the Gantt example hold one file for each ID, named by the ID alone. The maintained Gantt bundle is independent of this repository's history. Every revision in it, with all nodes that a later revision deleted, is built by executions of the current command line, with complete reads of ancestors, checks of the exact index and renewed source anchors for the verifier. The receipts and the ledger match the bundle, and the bytes of the example app and the node IDs are consistent through the whole history. The repository's documents and the planning recipes of the agent guide show node paths in this form. A rebuild leaves local experiments and the other Git history as they are.

`tests/test_ids.py`, `tests/test_core.py`, `tests/test_editor.py`, `tests/test_git.py` and `tests/test_gantt_git.py` cover fixed ID encodings and every value of the last byte, bodies without a heading and with Unicode text, the same path after creation and after a changed heading, rejected file names with a suffix or in other letter case, rejected format versions, collisions that differ only in letter case, the diagnosis of a wrong path in an editor document, and the rejection of a wrong path in the index or in a commit while the working tree is repaired. `tests/test_directory.py` covers that the nearest `.specspec` entry is taken, that directories with similar names stay unread and that editor documents and raw reads require exact node paths. The tests of the shared editor code and of the VS Code adapter cover creation messages, a creation form without a control for the file name, editing in the current format version alone, the recovery of drafts, the cues for Git and source changes and the exact file pattern of the custom editor. `example/gantt/history/verify.py` checks every commit of the maintained history, its receipts and the three stages whose model tests run.

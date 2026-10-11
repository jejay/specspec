---
id: 8afe8c39-6900-4f12-a2de-0dc6e41acf20
type: implementation
parents:
- d3bf2d3c-0172-4f67-807c-a73047018d83
sources:
- path: src/specspec/model.py
  symbol: ID_RE
- path: src/specspec/format.py
  symbol: parse_node, serialize
- path: src/specspec/workspace.py
  symbol: new_node, add_node, mutate, recover
- path: src/specspec/cli.py
  symbol: export_graph
- path: src/specspec/git.py
  symbol: git_snapshot, semantic_diff
- path: src/specspec/editor.py
  symbol: editor_request
- path: graph-ui-common/host/session.cjs
  symbol: GraphSession.handle
- path: vscode/package.json
  symbol: contributes.customEditors
- path: tests/test_core.py
- path: tests/test_repository_spec.py
---
# Inspect the identifier path and establish a clean local baseline

Read the original intention/design documents, repository graph tour, relevant
identity/file/schema/transaction/native-editor nodes and their ancestors. Inspect
Python records, parsing/serialization, workspace generation/mutation/recovery,
CLI export, Git snapshots/diffs, native document planning, shared host mutation
messages, VS Code file association and existing regression tests.

The investigation found UUID-only validation and double-hyphen filenames, creation
before the writer lock without collision retry, hyphen-only Mermaid escaping and
a UUID-era custom-editor glob. The separate encoding analysis records the RFC
padding conflict, filename alphabet constraint and unresolved conversion scope.
This record describes investigation, not an implemented compact-ID feature.

Local Windows baseline: all 86 Python tests passed; Ruff lint and format checks
passed; root (71 nodes before this change) and independent Gantt (44 nodes)
graphs passed warnings-as-errors validation. Shared UI, VS Code adapter and
Electron unit-test commands all exited successfully. No installed-host rendering
suite or remote CI run is claimed for this investigation.

The system Python lacks the development package; checks used the existing
.venv/Scripts/python.exe, without installing anything. Existing untracked local
VS Code settings and original emblem artwork were left untouched. Canonical
investigation nodes were added through the CLI, using the current UUID format
until the requested encoding conflict is resolved. Commits are explicitly
user-authorized; no Git hook is installed or replaced.

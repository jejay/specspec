---
id: OfBdhms=
type: implementation
parents:
- 79zOr-w=
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
- path: docs/own-spec.md
- path: README.md
- path: tests/test_directory.py
---
# Enforce ID-only node paths across the backend, hosts and fixtures

model.py selects current node format 7 while API_VERSION is 7. format.py
requires exact filename equality with <id>.md inside the sole .specspec directory.
workspace.py generates that path
inside the existing lock/collision/transaction boundary independently of body text.
CLI init/add and the library take binding fields directly. Human dependent labels
reuse Markdown headings. query.py prints full IDs in its complete parent headers.
Git node comparisons classify additions, semantic modifications and removals;
source-file rename tracking remains a separate source-resolution capability.

The shared creation form, persisted drafts and guarded host messages contain body,
type, parents and sources. VS Code's custom editor discovers ???????=.md resources;
Python validates their actual metadata and spelling. Both hosts negotiate the same
node version while keeping native text persistence distinct from managed writes.

The working self-graph and example snapshot have one ID-only file per identity.
The maintained independent Gantt bundle reconstructs every retained revision and
all earlier/deleted nodes with current CLI executions, complete ancestor reads,
exact-index checks and refreshed verifier source anchors. Receipts and ledger match
the bundle; runtime application bytes and historical node IDs stay consistent.
Current documentation, planning recipes and offline diagrams use the current path
contract. The original owner intention document remains an archival input. Local experiments and unrelated Git history stay intact.

Backend regressions cover fixed encodings/all final octets, headless/Unicode bodies,
creation and heading-edit path stability, rejected filename suffixes/case/version,
portable collisions, native invalid-path diagnostics and exact-index/historical
rejection despite a repaired working tree. Shared/adapter tests cover creation
messages, absence of filename controls, current-version editability, draft recovery,
Git/source cues and the exact custom-editor glob. Maintained-history verification
checks all retained commits, actual receipts and the three runnable model stages.

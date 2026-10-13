---
id: i7aT1lc=
type: implementation
parents:
- qowy5AI=
- evfMtUM=
sources:
- path: src/specspec/model.py
- path: src/specspec/format.py
- path: src/specspec/workspace.py
- path: src/specspec/cli.py
- path: src/specspec/editor.py
- path: tests/test_ids.py
- path: tests/test_core.py
- path: tests/test_recovery.py
- path: graph-ui-common/media/graph.js
- path: graph-ui-common/host/session.cjs
- path: graph-ui-common/view.cjs
- path: graph-ui-common/test/graph.test.cjs
- path: vscode/package.json
- path: vscode/src/host.js
- path: vscode/src/extension.ts
- path: electron/security.cjs
---
# Generate portable compact IDs throughout the backend and hosts

`ID_RE` and parsing enforce canonical padded five-byte Base64url and zero pad bits.
Workspace creation uses `secrets.token_bytes(5)` under the writer lock, retrying
exact/casefold collisions independently of summaries. Validation detects aliases.

CLI ID arguments retain full identities, including hyphen-leading IDs; Mermaid
injectively hex-encodes their ASCII. Cards/messages and the native-editor glob retain
`=`. Tests cover fixed byte vectors/all final octets, padding/alphabet errors,
collision timing, casefold aliases, filenames and CLI/editor/export identities.
Schema errors have current-format diagnostics. Existing presentation is project/view
scoped, with identity changes requiring explicitly preserved/copied user input.

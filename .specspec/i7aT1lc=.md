---
id: i7aT1lc=
type: implementation
parents:
- qowy5AI=
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
# Generate and check five-byte IDs in the backend and carry them in full through the editors

`ID_RE` in `model.py` and the parser in `format.py` accept an ID only as canonical padded Base64url of five bytes with zero pad bits. `new_node` in `workspace.py` draws `secrets.token_bytes(5)` while the writer lock is held and draws again on a collision, exact or apart from letter case. A node path is exactly `.specspec/<id>.md`. Validation checks the spelling of the full ID in the file name and reports IDs that differ only in letter case.

`cli.py` takes an ID argument in full, also when the ID begins with a hyphen. The cards and messages of the graph editors and the file pattern of the VS Code node editor in `vscode/package.json` keep the `=`. A schema error is reported with a diagnostic that describes the current format. The graph editors keep their presentation state for each project and view, and `vscode/src/host.js` isolates it by project root. `vscode/src/extension.ts` restores a stored draft only for the node ID it was written for, and after a change of ID the person preserves or copies the input explicitly.

`tests/test_ids.py` covers fixed byte vectors and every value of the last byte, errors of padding and alphabet, generation inside the lock with a new draw on each collision, IDs that differ only in letter case, file names, and IDs passed through the command line and the editor backend.

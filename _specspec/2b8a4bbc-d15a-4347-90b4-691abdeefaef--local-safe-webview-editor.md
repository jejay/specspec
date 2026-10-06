---
id: 2b8a4bbc-d15a-4347-90b4-691abdeefaef
type: requirement
status: proposed
parents:
- adb5a4c8-f9c5-4bcc-b38b-8584d469cf25
- 6c457b0a-654e-4545-a4b4-667f467be4f3
managed_hash: a755eec845edbc52f96888bf6f90fbe7e3bb8c5713c68f0c6ae83759e6c69c49
---
# Render and edit through a local VS Code webview

Render local node cards and SVG relationships in a nonce-protected webview. Use DOM
text APIs for project content and no remote renderer. Provide binding-text, parent,
and source-reference forms backed by the Python CLI; acceptance and retirement
remain separate confirmed actions.

Make historical comparisons read-only, prohibit tool execution in untrusted
workspaces, and retain unsaved form content on refresh/errors. Subscribe to Git
state and canonical-file changes without staging or committing for the user.

Origin: [CONCLUSION_SPEC.md](../CONCLUSION_SPEC.md), VS Code extension.

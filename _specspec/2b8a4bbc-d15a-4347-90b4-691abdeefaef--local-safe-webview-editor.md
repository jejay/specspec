---
id: 2b8a4bbc-d15a-4347-90b4-691abdeefaef
type: requirement
parents:
- adb5a4c8-f9c5-4bcc-b38b-8584d469cf25
- 6c457b0a-654e-4545-a4b4-667f467be4f3
---
# Render and edit through a local VS Code webview

Render local node cards and SVG relationships in a nonce-protected webview. Use DOM
text APIs for project content and no remote renderer. Provide binding-text, parent,
and source-reference forms backed by the Python CLI. Save nodes without an approval
stage; withdrawal/restoration remain separate confirmed actions, not acceptance.
Offer the guarded CLI migration for a legacy workspace, keeping its forms read-only
until conversion and preserving any existing dirty draft with its original node contents.

Make historical comparisons read-only, prohibit tool execution in untrusted
workspaces, and retain unsaved form content on refresh/errors. Subscribe to Git
state and canonical-file changes without staging or committing for the user.

Origin: CONCLUSION_SPEC.md and the user's risk-proportionate-review correction.

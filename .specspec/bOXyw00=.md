---
id: bOXyw00=
type: requirement
parents:
- LvYBN_4=
---
# Use a literal local webview with guarded graph actions

Render native DOM node cards and SVG relationships in a nonce-protected local
VS Code webview. Project text uses DOM text APIs. Bundle the renderer and assets
locally with strict CSP. The Python backend plans binding-text, parent and source
changes and validates canonical mutations.

Trusted working views enable applicable save/add/delete/source actions; historical
views provide copyable read-only details. Graph-invalid reloads retain input while displaying fresh broken relationships
and diagnostics. Unavailable loads retain marked last-usable context. Subscribe to canonical and Git notifications.
The owner controls staging, commits and hook setup through normal Git workflows.

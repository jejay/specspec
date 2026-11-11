---
id: -DClehg=
type: requirement
parents:
- GQdmCrA=
---
# Save the focused node form with Ctrl+S or Command+S the way its Save button does

Ctrl+S on Windows and Linux and Command+S on macOS submit the form of the focused node, with the same enabled state and the same content as its Save button. The shortcut works from the text field, from the parent and source settings and from the rest of the focused card, and it works for a new node. It saves the way the form saves: a node-file editor in VS Code saves its document through VS Code, and a graph panel and the desktop app save through the Python writer.

The page captures the shortcut before the text field and the forwarding of webview shortcuts handle it. The shortcut respects the restrictions of the Save button: a comparison that is still loading, a read-only view, an invalid state, a pending request and a deleted node. A held key saves once. An open modal dialog and a draft that waits in the overview are left alone. A save by shortcut asks before it overwrites a node that changed outside the draft, recovers from an error with the draft kept, and leaves undo in a node-file editor with VS Code.

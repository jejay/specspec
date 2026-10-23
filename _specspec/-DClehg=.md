---
id: -DClehg=
type: requirement
parents:
- GQdmCrA=
---
# Save focused node forms through the existing host save path

Ctrl+S on Windows/Linux and Command+S on macOS submit the focused node editor using
the same enabled state and payload as its Save button. The shortcut works from
binding text, parent/source settings and focused-node chrome, including new nodes.
It preserves the current form's save owner: VS Code bound files use native document
save, while project panels and Electron use managed mutations.

Capture the shortcut before editor/webview forwarding. Honor provisional,
read-only, invalid, pending and deleted-node restrictions, suppress repeated saves,
and leave modal dialogs and overview drafts independent. Existing overwrite
confirmation, error recovery, draft retention and native undo ownership remain.

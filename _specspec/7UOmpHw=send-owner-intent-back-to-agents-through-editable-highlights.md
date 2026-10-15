---
id: 7UOmpHw=
type: requirement
parents:
- DG-JpDc=
---
# Send owner intent back to agents through editable highlights

Both VS Code and Electron let owners Shift-click node chrome to cycle through the
available spotlight colors and then unhighlighted. Ctrl+Shift-click unhighlights
one node; Command+Shift-click supplies the macOS equivalent. Clear highlight in
the Spotlights dropdown clears the entire highlight set.

Applying a retained spotlight produces the same editable highlights as manual
clicking. Owners can cycle, remove and add members regardless of their origin,
while the retained spotlight stays immutable. From any nonempty highlight set,
Create spotlight from highlights asks for one message and publishes a new local
spotlight. The external agent reads its message, full node IDs, colors and exact
versions with spotlight show, giving the owner a backchannel without copying IDs.
Native editing, drafts and ordinary navigation retain their independent behavior.

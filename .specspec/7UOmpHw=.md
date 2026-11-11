---
id: 7UOmpHw=
type: requirement
parents:
- DG-JpDc=
---
# Let the owner answer an agent by highlighting nodes and saving them as a spotlight

In both graph editors the owner Shift-clicks a node card, outside its inputs and controls, to switch its highlight on or off, and all highlights share a single ink. Ctrl+Shift-click, or Command+Shift-click on macOS, removes one node from the set. Clear highlight empties the whole editable set. Inputs and controls inside a card keep their own clicks with modifier keys.

Applying a stored spotlight gives the same editable highlights as clicking by hand. The owner adds or removes nodes while the original spotlight stays immutable. Create spotlight from highlights asks for one message and captures the current comparison. The agent reads the messages, the IDs, the comparison, the status of each node and the advisory warnings about the working files with `specspec spotlight show`. Editing, drafts, ordinary navigation and saving work independently of the highlights.

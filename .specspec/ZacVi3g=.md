---
id: ZacVi3g=
type: requirement
parents:
- 6Bk988A=
- YOPhqYc=
---
# Bundle one editable unified diff control for both hosts

Use CodeMirror's unified merge editor in the shared renderer to mimic familiar
inline revision editing within the expanded node card. Bundle pinned dependencies
and licenses locally; keep project text literal and styling inside the local CSP.
This portable control supplies an editable target, red original-text blocks,
green inserted lines, character highlights, line numbers and a change gutter.
Theme tokens supply revision colors with standalone defaults and contrast cues.

Compare the current form body, including an unsaved draft, against the selected
comparison's base body. Added nodes compare against empty text. Unchanged bodies
remain plain. New-node drafts and working-only provisional reads show ordinary
editing until a comparison is available. Deleted ghosts retain their copyable
base body, read-only. Historical target comparisons show inline changes read-only.

Refreshing the baseline preserves draft text, selection, focus and managed undo.
Changing resources gives each form a fresh editor history. VS Code native file
forms route undo and redo to the TextDocument; managed project and Electron forms
use the editor's local history until their existing save operation. Saved bodies,
native edit messages and draft recovery contain target text only. Original text
blocks are derived presentation. Parent/source controls retain their own forms.

The unified control is chosen for a locally bundled, host-neutral editing surface;
it mimics inline editor behavior while each host retains its document lifecycle.

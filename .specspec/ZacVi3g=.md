---
id: ZacVi3g=
type: requirement
parents:
- 6Bk988A=
- YOPhqYc=
---
# Edit and compare a node's text in one unified diff control that both editors bundle

The shared renderer uses the unified merge editor of CodeMirror inside the expanded node card. It is chosen because it is bundled locally and works the same in both graph editors: it mimics the inline editing of changes that is familiar from VS Code, while each editor keeps its own lifecycle of documents. Its dependencies have pinned versions and are bundled locally with their licenses. Project text stays literal, and the styling works within the local content security policy. The control supplies an editable current text, red blocks of original text, green inserted lines, highlights of changed characters, line numbers and a change gutter. Theme tokens supply the colors of changes, with defaults for the standalone app and with contrast cues.

The control compares the text in the form, including an unsaved draft, with the text that the node has in the base of the selected comparison. An added node is compared with empty text. A text without changes appears plain. The draft of a new node and a working graph whose comparison is still loading show ordinary editing until a comparison is available. A deleted node keeps the text of its base, which can be copied and is read-only. A comparison whose target is a commit shows the inline changes read-only.

A refresh of the base keeps the draft text, the selection, the focus and the undo history of the form. Moving to another node gives the form a fresh history. In a VS Code node-file editor, undo and redo go to the `TextDocument`. In a graph panel and in the desktop app the form uses the control's own history, and the save operation of the form persists its text. A saved text, an edit message to a VS Code document and a recovered draft contain the current text alone, and the blocks of original text are derived for display. The controls for parents and for sources are separate fields of the form.

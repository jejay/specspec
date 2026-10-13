---
id: GQdmCrA=
type: requirement
parents:
- HV8tZho=
- YOPhqYc=
- Bnr6yZY=
---
# Bind native node-file editors and independent graph views

Contribute the default custom text editor for `**/_specspec/???????=*.md`, resolving
the actual node/project through Python. Each file tab edits its bound resource and
shows graph context. Neighbors open their own files. Raw Markdown is accessible
through Reopen Editor With. Split views share TextDocument contents and keep their
own cameras/focus. Open Graph/project selection and historical comparisons use
independent main-editor panels.

Python overlays validated open-document text onto existing files and returns one
Markdown edit plan with diagnostics. VS Code applies WorkspaceEdit and owns native
save/autosave/undo/redo/dirty recovery. Invalid text remains repairable with a marked
last valid graph. Managed project actions require clean SpecSpec documents. Missing
files reject edits and overlays skip absent buffers after validating their inputs.

Electron uses the shared renderer/session and managed Python save adapter. Native
text saves and journaled project mutations have their respective persistence
boundaries; native Save can persist invalid text like the raw Markdown editor.
Retain unapplied form input with resource/view-scoped recovery and explicit handling.

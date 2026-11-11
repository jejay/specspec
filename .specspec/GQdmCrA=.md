---
id: GQdmCrA=
type: requirement
parents:
- HV8tZho=
- YOPhqYc=
- Bnr6yZY=
---
# Bind each VS Code node-file editor to its document and open graph panels independently

The VS Code extension contributes the default custom text editor for files that match `**/.specspec/???????=.md`, and Python resolves the actual node and its project. Each such tab edits the file it is bound to and shows that node in its graph context. Selecting a neighbor there opens the neighbor's own file, while a graph panel moves its focus to the neighbor. Reopen Editor With gives the raw Markdown. Split views of one file share the contents of its `TextDocument` and keep their own cameras and focus. Open Graph, the selection of a project and comparisons between commits use independent panels in the main editor area.

For a node-file editor Python lays the validated text of the open documents over the files that exist and returns one planned edit of the Markdown together with diagnostics. The body in the form uses LF, and the planned text keeps the newline style of the bound document and names the exact text it replaces. A complete planned document that lacks a final newline receives one, and the empty body of a repair form stays empty. VS Code applies the plan as a `WorkspaceEdit` and owns saving, autosave, undo, redo and the recovery of unsaved documents. Text that makes the graph invalid shows the current relationships with their diagnostics and stays editable, and a file that cannot be read stays reachable as raw Markdown for repair. An action that the Python writer performs on the project requires that no open specspec document has unsaved changes. An edit to a missing file is rejected, and an open buffer without a file is validated and then left out of the overlay.

The desktop app uses the shared renderer and session and saves through the Python writer. A save of a VS Code document and a journaled change of the project through the writer are two separate ways of persisting, and Save in VS Code can persist invalid text as the raw Markdown editor does. Form input that is not applied to its document yet is kept for recovery per file and per view, and the owner decides explicitly what happens to it.

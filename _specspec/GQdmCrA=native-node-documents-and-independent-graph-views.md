---
id: GQdmCrA=
type: requirement
parents:
- HV8tZho=
- YOPhqYc=
- Bnr6yZY=
---
# Bind node-file editors to native documents through portable host adapters

Contribute a default custom text editor for **/_specspec/???????=*.md. Resolve the actual project and node through the Python backend rather than trusting the glob or filename alone. A node-file tab edits its associated resource and displays surrounding graph context; opening another node opens its file editor. Multiple views of the same working file share TextDocument contents, while cameras, focus and comparison state belong to each view. Keep raw text available through Reopen Editor With. Remove the Activity Bar container; Open Graph and project selection open independent main-editor panels. Historical comparisons use independent read-only panels and never edit working-file documents or check out commits.

Keep one renderer and shared guarded sessions. Split project-level document coordination from per-view presentation. Add a non-writing Python editor operation that overlays open document text on saved project files, plans Markdown changes and supplies graph/schema diagnostics. Preserve comments, extensions, identity and binding text; reject unsafe paths and never create canonical files in the planner. Hosts do not fork graph rules or YAML serialization. File deletion, invalid text and pending backend errors retain user input and give actionable diagnostics.

In VS Code, form changes update the bound TextDocument with WorkspaceEdit; native save, autosave, undo/redo, dirty state and recovery own ordinary file persistence. This deliberately revises the earlier Python-only visual-editor writer choice for these document saves: they are not Python-locked or journaled multi-file transactions, and a custom text provider cannot guarantee a save veto or full-DAG consistency against arbitrary external writers. Unsaved buffers may be structurally invalid like raw Markdown; show diagnostics and retain the last valid graph, while permitting repair of the bound form. Project-wide CLI mutations remain validated/journaled and refuse to run over affected dirty documents. Do not silently overwrite dirty text buffers.

Electron retains its isolated preload/main adapter and Python-managed save path; no VS Code imports enter common code and no renderer fork is introduced. Shared edit planning and view/session protocols are the portability boundary, not a demand that Electron emulate every native VS Code document feature in this first slice. Scope per-view presentation and retained drafts by project and view identity, not just project root.

Origin: the user's explicit request to try the custom-text/document-adapter design after clarifying main-editor access and useful multiple graph tabs. Native text persistence and the project/view split are revisable choices, not implications silently imposed on the original user intention.

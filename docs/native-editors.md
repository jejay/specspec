# Native node-file editors and portable graph views

Opening `**/_specspec/???????=*.md` defaults to **SpecSpec Graph** in VS Code's main
editor area. The filename glob is discovery only: Python resolves/validates the
actual node. **Reopen Editor With → Text Editor** remains available, and user
editor associations can override the default. There is no Activity Bar container.

A file tab edits its associated node in graph context. Selecting a neighboring
node opens that node's custom editor; **Total graph** changes the current view,
not the resource being saved. **Open Graph** opens an independent project panel
with node creation and managed project actions. Commit comparisons open separate
panels; commit targets are read-only and never check out or modify working files.
A comparison with an empty target shows the workspace/open-document graph.

## Documents, projects, and views

- VS Code owns each `TextDocument`: dirty state, file save/autosave, undo/redo,
  close prompts, and native document recovery. Split editors share that document.
- `ProjectDocuments` coordinates per-project edit planning and guarded CLI writes.
  Open native document text overlays saved files when computing graphs and Git
  differences, including changes made in raw Markdown editors.
- Each `GraphSession`/webview owns its camera, focus, and comparison selection.
  Per-panel webview state remains scoped to its project. Different node editors
  and split views do not share cameras. Project watchers are reference-counted.
- Electron continues to use the same renderer/session with its existing isolated
  host, retained form drafts, and Python-managed save path. The common code imports
  neither host SDK. Electron does not need a VS Code `TextDocument` implementation.

Custom-text resolution returns without waiting for the webview render handshake:
VS Code must finish wiring the editor before all its messages are deliverable.
Initialization errors are reported in notifications/Output, with a raw-Markdown
escape for unparseable nodes.

## Editing and persistence

Form input immediately sends a document-edit request, with rapid pending typing
coalesced to the latest form. The backend plans changes against current document
text. The host applies a minimal `WorkspaceEdit`, without splitting CRLF or UTF-16
surrogate pairs, respecting the native document's line-ending convention. Body-only changes leave frontmatter bytes intact; equivalent
unordered parent/source lists do not rewrite untouched comments/order. Sequence
acknowledgements prevent an older result from clearing newer input. A native save
waits for already-received form edits; this is not a guaranteed save veto.

Other-view/raw-editor changes require confirmation before a stale form overwrites
changed fields. A version/text change during planning refuses the edit. Saving an
unchanged form after native undo/redo needs no spurious overwrite confirmation.
Native undo/redo is routed to the document rather than a second browser-only undo
stack. The same underlying document updates every graph view.

Applied changes use VS Code's recovery. Unapplied/rejected form input additionally
has a per-view, per-resource workspace-state backup. Reopening the file can show
that recovered form for copy, explicit save/conflict confirmation, or discard;
it is not silently applied or claimed to be a dirty native document. Save/copy any
old Activity Bar form draft before restarting into this version: old sidebar
webview state is not automatically migrated into new file tabs. Live sibling
views' pending forms are not mistaken for abandoned recovery records. This is not
an unlimited draft archive or a claim of power-loss durability before IPC/storage
completes. Project panels retain the existing managed-form state; automatic
restoration of arbitrary project/history panels after a workbench restart is not
implemented in this slice.

Unsaved native buffers may be invalid, just like raw Markdown. Diagnostics keep
the last valid graph marked out of date while the bound form remains editable for
repair. Incomplete sources JSON is retained as an invalid frontmatter value until
completed. A wholly unparseable node can be repaired in Text Editor. Native Save
can persist invalid text: validate before committing. Project-wide CLI writes
refuse dirty open SpecSpec documents; they retain the existing validation, locks,
original-byte checks, journal/recovery and do not silently overwrite buffers.

**Important choice:** native text-document saves are not Python-journaled graph
transactions. Python remains authoritative for graph/schema meaning and proposed
Markdown, but VS Code persists its text buffers. Full-DAG validity cannot be
promised across arbitrary native/external saves or concurrent raw editing. Electron
and explicit CLI project operations still use the managed Python writer. No new
format metadata, hashes, approval stages, Git staging, or commits are introduced.

## Non-writing Python API

The hidden `specspec api` integration adapter consumes bounded API-6 JSON on stdin:

```json
{
  "api_version": 6,
  "op": "plan",
  "documents": {"_specspec/Zm9vYmE=summary.md": "---\n..."},
  "edit": {
    "path": "_specspec/Zm9vYmE=summary.md",
    "id": "Zm9vYmE=",
    "body": "# Updated binding text\n",
    "parents": ["ZnJlc2g="],
    "sources": "[]"
  }
}
```

Use `op: "read"` without `edit` for a graph read; optional `base: "HEAD"` requests
comparison. Electron uses the same operation without native overlays. `sources` in a
plan is JSON text for implementation nodes; shared forms may send neutral
`[]` for other types without adding a sources field. The backend uses the current
text's type, including raw-editor changes, not an initial tab type. No `retired`
field/edit exists. Delete is a confirmed managed project-file operation requiring
clean SpecSpec documents, not a native metadata change pending Save. The result has `snapshot`, `changes` (`path`, exact `before`/`after` text), optional
compact `diff`, and `note`; structured diagnostics are in the envelope.
Invalid buffers are successful reads/plans with `snapshot.valid: false` and
explicit diagnostics, not successful graph validation. Unsafe paths, edits to
missing files, identity changes, unsupported schemas, locks/recovery and oversized
requests fail. Delete now removes every descendant, including shared children,
through the same backend plan as the CLI. Its confirmation shows the total file
count and uncommitted affected-node warnings (staged is not committed), then
rechecks the reviewed scope under the writer lock. Dirty descendant documents
remain protected by the project-wide save/revert guard. Reads skip overlays for already deleted files, so retained open
buffers do not resurrect nodes. The planner never writes files or recreates a
deleted node. The current application protocol is API 6 with shortcut-free node format 6;
upgrade the CLI and both host builds together. See [compact commands](cli.md).

## Verification

Python tests cover byte/comment/extension preservation, overlays, invalid-buffer
repair, graph rules, missing/unsafe paths, runtime locks, bounds and unsaved Git
comparisons. Shared tests cover coordination, coalescing, minimal edits, sequence
acknowledgements, caret/drafts and managed-host regression. Adapter tests cover
native edits/save, independent panels, dirty-document protection and unapplied-form
recovery. The installed-host runner uses the maintained current-schema Gantt graph for
canvas/Git/watcher regressions and a compact nested graph for native lifecycle,
split/camera/undo/raw-edit/repair checks. It does not depend on old self-spec IDs
or historical schemes. Those are separate scale boundaries, not a large-graph typing
performance guarantee. Electron's managed save/deletion behavior uses its own real
host suite. See implementation records for actual runs; configured CI is not
locally observed remote execution.

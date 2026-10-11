---
id: _ANZHCw=
type: implementation
parents:
- GQdmCrA=
- YOPhqYc=
- LvYBN_4=
sources:
- path: src/specspec/editor.py
  symbol: 'editor_request: overlays, edit plans and diagnostics'
- path: src/specspec/cli.py
  symbol: editor command
- path: graph-ui-common/host/documents.cjs
  symbol: ProjectDocuments and minimalTextEdit
- path: graph-ui-common/host/session.cjs
  symbol: native document port, coalescing and applied-version acknowledgements
- path: graph-ui-common/media/graph.js
  symbol: bound-file forms, caret, recovery and native undo
- path: graph-ui-common/test/documents.test.cjs
  symbol: planning and read/apply races
- path: graph-ui-common/test/session.test.cjs
  symbol: typing coalescing and document acknowledgements
- path: graph-ui-common/test/graph.test.cjs
  symbol: native forms, recovery and late peer acknowledgements
- path: graph-ui-common/test-host/ui.cjs
  symbol: CDP context lifecycle and bounded discovery
- path: vscode/package.json
  symbol: default custom editor contribution
- path: vscode/src/extension.ts
  symbol: GraphEditors, GraphProject and GraphView
- path: vscode/test/extension.test.cjs
  symbol: adapter lifecycle, dirty buffers and unapplied recovery
- path: vscode/test-host/documents.cjs
  symbol: installed native document tests
- path: vscode/test-host/smoke.cjs
  symbol: extension-host document service
- path: vscode/test-host/run.cjs
  symbol: full canvas and compact nested/CRLF fixtures
- path: tests/test_editor.py
  symbol: non-writing API and current-type rules
- path: docs/native-editors.md
  symbol: persistence and verification boundaries
- path: electron/main.cjs
  symbol: unchanged managed GraphSession host
---
## Current compact-ID and history correction

The implementation/verification below records earlier revisions. Its legacy-reader,
schema-migration, original API-2 receipt and root-history compatibility descriptions
are superseded by qowy5AI= and YaXJpGE=. Current production code supports only the
canonical Base64url node scheme, with no old-schema reader or migration command.
The default node-editor association is **/_specspec/???????=*.md. Gantt's maintained
history is rewritten and bundled; tests do not require old root graph revisions.
Earlier run counts are historical evidence, not claims about this revision. The
separate current implementation record documents the new checks and limitations.

# Implement native node-file editors with portable graph sessions

VS Code contributes a default CustomTextEditorProvider for **/_specspec/*--*.md and removes the Activity Bar container. GraphEditors resolves actual backend nodes, GraphProject shares document coordination/watchers, and GraphView keeps independent presentation. File tabs edit their bound resource; neighbors open their node files. Open Graph creates project panels; comparisons create independent panels and commit targets remain read-only, including when workspace overlays are invalid. Raw Markdown remains accessible, with an escaped fallback for nodes that cannot be loaded.

Python's non-writing editor API overlays existing file text, plans one document edit and returns schema/DAG diagnostics. It preserves body-only frontmatter bytes, comments/extensions, unordered reference lists and CRLF/Unicode; role-specific sources rules use current text rather than an initial tab type. Invalid buffers can be repaired without pretending they are valid graphs. Missing/unsafe files, identity changes, recovery/locks, legacy mutations and bounds are guarded; no files are written or recreated by this planner.

Shared ProjectDocuments serializes planning and guarded project writes, refuses dirty-buffer CLI mutations, and checks versions/actual text before and after native apply. Overlay reads reject results made stale during loading instead of labeling old text with a new document version. GraphSession coalesces pending typing and acknowledges applied versions/sequences; late acknowledgements cannot overwrite newer input or peer snapshots. The renderer keeps native caret/form DOM and routes undo/redo to the document. Native Save/autosave/dirty/undo/recovery belong to VS Code, not Python's transaction journal. Unapplied form input has separate per-view/resource workspace-state recovery; it is never silently replayed or mislabeled as native dirty text.

Electron uses the identical renderer/session with its existing sandbox/preload and managed Python-save adapter. It does not need a VS Code SDK or a duplicate domain engine. Project/history panels keep managed operations, while ordinary native file saves deliberately have different persistence guarantees. This is an implementation attempt, not proof that every filesystem race, workbench restart or large-graph typing workload is solved.

Verification: all 86 Python tests, 99 shared tests, 37 VS Code adapter tests and nine Electron unit tests pass; Ruff check/format and graph validation pass. The installed Windows VS Code suite passed on the repository-sized 70-node target/71-node display fixture, plus a compact three-node nested graph for default associations, native dirty/save/undo/redo, raw editing, invalid-buffer repair, split synchronization, independent cameras, different node tabs and CRLF/Unicode saves. Main-editor and independent-tab screenshots were inspected. The installed Windows Electron suite passed the same full canvas/paint/watcher tests plus actual managed save, retained external-change drafts, reload/history and sandbox/network boundaries. These fixtures precede adding this evidence node; no fixed graph-count invariant is introduced.

Remaining boundaries: large-graph typing performance is not established by compact lifecycle tests. Native saves can persist invalid text and do not guarantee a full-DAG save veto, locks or journals. Arbitrary project/history panels are not automatically restored after workbench restart. Invalid cold-open nodes may need Text Editor repair. Unapplied backups do not guarantee power-loss durability before IPC/storage completes; old sidebar webview drafts are not automatically migrated, so save/copy them before restarting. Native overwrite/selection dialogs and migration are primarily adapter/shared-session evidence, not exhaustive real-host manual flows. Linux/macOS and remote CI are not claimed locally executed. At the initial implementation checkpoint no files were staged or committed. Hooks were not installed, and original artwork/local settings remained untouched.

## Repository dogfooding and commit authorization

The user subsequently asked to ensure this repository uses SpecSpec for this change and explicitly authorized committing it. The active graph already records the corrected main-editor intention, separate revisable native-document conclusion, withdrawal of sidebar hosting with live dependents reconnected, and linked implementation/evidence. This is an actual CLI-maintained repository specification change, not only prose in external documentation. The complete intended graph, backend, shared UI, adapter, tests and documentation are committed together after exact-index checks of the root and nested example graphs. Local settings and original artwork are excluded; hooks are not installed or replaced. A commit records the attempt and its evidence, not approval or proof that the choice is permanent/correct.

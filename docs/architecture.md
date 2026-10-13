# Architecture: an engineer's map

[Open the control and data flow SVG](architecture.svg) at full size and zoom in.
Read **A** for ownership, **B** for refreshes, **C** for persistence, and **D** for
change locations. Paths in the diagram are repository-relative; arrows summarize
architectural flows rather than every function call.

![SpecSpec runtime architecture, refresh flow and two edit lifecycles](architecture.svg)

This documents the current implementation, not a new product decision. The
[specification tour](own-spec.md) and tool-managed [`_specspec/`](../_specspec/)
graph explain the intentions, revisable choices and superseded designs. Some
implementation records retain historical descriptions; read their later
corrections rather than treating those descriptions as current contracts.

## The mental model

- **Canonical data is a Markdown DAG, not a database.** Each direct
  `_specspec/<id><slug>.md` file has strict YAML frontmatter and a binding body.
  `parents` stores incoming links; the graph has one manifesto, requirements with
  potentially multiple parents, and terminal implementations. Only format/API 5
  and padded five-byte Base64url IDs, including the final `=`, are supported.
- **Python owns domain meaning.** Schema, graph rules, physical deletion, Markdown plans,
  managed transactions and Git comparisons are shared by the CLI and both UIs.
  No host reimplements those rules. Each CLI invocation rebuilds snapshots;
  there is no daemon or persistent graph index.
- **One shared UI has two persistence lifecycles.** Electron and VS Code project
  panels use Python-managed writes. VS Code node-file editors apply non-writing
  Python plans to native text documents. These saves are deliberately *not*
  Python transactions.
- **Presentation is not specification.** Cameras, focus, colors, layout and drafts
  do not enter canonical metadata. Graph depth is not confidence; withdraw by
  deleting node files, with reasons/earlier explanations in Git. Deleted HEAD nodes
  remain D through staging and disappear after commit; no retired status exists. Agent context is implemented as CLI
  exports; Claude Code/Codex connectors are not implemented.

## A. Follow the runtime boundaries

| Layer | Start reading here | Responsibility |
| --- | --- | --- |
| Browser canvas | [`graph.js`](../graph-ui-common/media/graph.js), [`graph-model.js`](../graph-ui-common/media/graph-model.js), [`graph-camera.js`](../graph-ui-common/media/graph-camera.js), [`view.cjs`](../graph-ui-common/view.cjs) | Literal DOM text/native forms, SVG curves, revision overlays, metrics, Dagre layout and D3 navigation. Calls `window.SpecSpecHost`; cannot access project files or spawn tools. |
| Shared host coordination | [`session.cjs`](../graph-ui-common/host/session.cjs), [`documents.cjs`](../graph-ui-common/host/documents.cjs), [`cli.cjs`](../graph-ui-common/host/cli.cjs) | Per-view `GraphSession`, project-level `ProjectDocuments`, serialized work, conflict guards, render handshakes and bounded subprocess invocation. No VS Code/Electron SDK imports. |
| Host adapters | [`vscode/src/extension.ts`](../vscode/src/extension.ts), [`electron/main.cjs`](../electron/main.cjs), [`electron/preload.cjs`](../electron/preload.cjs) | Trust, project discovery, dialogs, file/Git notifications, assets, messaging and presentation storage; VS Code also supplies native documents. |
| Python backend | [`cli.py`](../src/specspec/cli.py), [`workspace.py`](../src/specspec/workspace.py), [`format.py`](../src/specspec/format.py), [`model.py`](../src/specspec/model.py), [`graph.py`](../src/specspec/graph.py) | Click dispatch, byte snapshots, version bootstrap, strict schema/round-trip YAML, normalized records, adjacency maps, deterministic ordering and iterative traversals. |
| Operation-specific I/O | [`editor.py`](../src/specspec/editor.py), [`git.py`](../src/specspec/git.py), [`workspace.py`](../src/specspec/workspace.py) | Unsaved overlays/edit plans, Git snapshots/diffs/source impact, and lock/stage/journal/recovery respectively. All reuse the snapshot/schema/graph engine. |

The bridge spawns the trusted executable with argument arrays, `--root`, and
`shell: false`. Bodies or editor requests go through UTF-8 stdin. JSON stdout has
`{api_version: 5, ok, result, diagnostics}`; process time and output are bounded.
CLI exits are 0 for success, 1 for invalid/rejected operations, and 2 for invocation
or I/O failures. An editor plan can succeed while reporting
`snapshot.valid: false`: it preserves repairable intermediate text, not a valid
graph claim.

`list`, `show`, `context`, `impact` and `export` are read-side CLI entry points for
engineers and agents. `context` includes the selected node and complete ancestor
closure; immediate children/live siblings are optional. A byte budget reports
omitted optional IDs and fails rather than truncating required binding text.

The renderer uses local assets and a nonce-protected CSP, inserting project text
through `textContent`/`value`, never executable Markdown. Electron's
[`security.cjs`](../electron/security.cjs) restricts assets, actions and IPC senders;
its sandboxed/context-isolated preload exposes no general filesystem, process or
IPC API. VS Code requires workspace trust before invoking the tool.

## B. A read/refresh round trip

1. Host notifications call `scheduleRefresh()`. VS Code's reference-counted
   `GraphProject` watches canonical files and listens for document/Git changes.
   Electron's [`GraphWatcher`](../graph-ui-common/host/watch.cjs) watches the project
   parent and node directory, reattaching after directory replacement. Events are
   hints, not a change log. The session coalesces bursts and retries transient reads;
   configurable polling defaults to **0/off**, and explicit Refresh remains.
2. Working VS Code views use `ProjectDocuments.readGraph()` → `editor --json`,
   overlaying all open node-document text on saved files. Electron uses `export`
   and then a selected-base `diff` where available. A commit target instead uses
   `diff --base ... --target ...`: it never checks out files or consumes invalid
   working buffers. A valid workspace graph can still display with a
   **diff-unavailable** note when its baseline cannot be read.
3. Identical automatic-refresh payloads do not redraw. Invalid reads preserve the
   last valid graph, explicitly mark it out of date, retain input and disable
   managed mutations. Bound native forms remain available for repair. No invalid
   external file is automatically rewritten.
4. The renderer combines base/target records and added/removed relationships for
   display. That union can contain cycles, so path metrics use each **complete
   individual revision**, never the union or focused subset. Dagre's placement
   backbone is only a layout aid: it does not remove canonical or displayed links.
   Intrinsic card sizes/relationships determine world layout; viewport/camera
   changes do not reflow the graph.
5. Startup waits for `ready`; a snapshot carries a `renderToken`. The renderer
   returns `rendered` with the token, visible IDs and count. `renderMatches()`
   checks complete overview/neighborhood membership. Timeouts/client failures
   become visible errors. These are sequence/membership checks, not content hashes.

Drafts retain original node records. An unrelated graph change does not invalidate
an edit; a managed same-node overwrite asks for confirmation, and a deleted draft
stays copyable instead of recreating the file. Cameras are per view/scene; split
native editors share text, not cameras.

## C. Two edit paths — do not collapse them

### Managed commands: CLI, Electron, VS Code project panels

UI sessions check authorization, current node IDs and draft conflicts, then build
specific CLI commands; renderers cannot supply arbitrary commands or file paths.
Direct CLI calls do not run the UI workflow; warned CLI deletion asks one terminal
confirmation or requires explicit `--yes` for JSON/noninteractive calls.

[`deletion.py`](../src/specspec/deletion.py) plans the full directed descendant
closure, including shared children, and derives per-node Git warnings without
optional index writes. Both hosts use `delete --dry-run --json`, show the total
scope/warnings, then pass a reviewed plan to the managed command. It recomputes
scope/paths/warnings under the lock and refuses changed scope rather than silently
deleting more nodes. This is destructive-action consent, not node review approval.
See [deletion](deletion.md) for warning, native-document and Git-status limitations.

`workspace.mutate()` acquires the managed-writer lock, reads/validates the current
snapshot, constructs and validates a candidate, stages replacements and journals
old/new bytes in **`.specspec-local/`**, outside the canonical directory. It compares
original bytes before replacement, calls `os.replace()` for replacement bytes or
unlinks files with `new: null` for the complete deletion closure, validates the
result and cleans transaction state on success. The UI then reloads the graph.
`init` instead stages an entire new node directory and refuses an existing graph.

An interrupted batch leaves explicit recovery state. `recover` only restores files
whose current bytes match known original/replacement states; it refuses intervening
external edits. Retain journals, and remove a stale lock only after confirming no
writer runs. These are process-interruption protections, not atomic multi-file
replacement, full power-loss durability or adversarial filesystem guarantees.

### VS Code node files: plan → buffer → native Save

Form typing sends sequence-numbered `edit` messages. `GraphSession` coalesces them;
`ProjectDocuments` serializes planning against current open buffers. Python's
`editor_request()` overlays document text and returns exact `before`/`after` text,
a snapshot and diagnostics **without writing files**.

The host checks document text/version, applies a minimal `WorkspaceEdit` without
splitting CRLF or UTF-16 surrogate pairs, and acknowledges the applied version.
VS Code owns dirty state, shared split-document contents, undo/redo, Save/autosave
and applied-document recovery. Already-received form edits are drained before a
native save; that is not a schema veto. Unapplied/rejected forms have a separate
per-view/resource `workspaceState` backup, not a silently diverging second document.

**Native Save can persist invalid text and acquires no Python writer lock/journal.**
Managed VS Code project mutations refuse dirty open SpecSpec documents. See
[native editor semantics](native-editors.md) for repair, conflict and recovery limits.
Electron intentionally retains the managed-save path.

## Git is another snapshot source, not another writer

[`git.py`](../src/specspec/git.py) reads commit trees or the **exact staged blobs**
through Git, then passes those bytes into the same snapshot engine. `hook check`
validates the index, not repaired/unstaged working files; hook installation is
opt-in and preserves existing hooks. Ordinary exploration never stages, commits or
switches branches.

Semantic diffs match full IDs, distinguishing body/parent/metadata
changes from pure filename renames and raw file changes. They return both snapshots
and edge additions/removals. Structural impact includes descendants from **both**
old and new graphs, so removing an edge cannot hide its earlier dependents.
Changed linked source paths identify implementation nodes and their ancestors,
using references from both snapshots. Source-only impact is not node modification;
source symbols are descriptive, not language-resolved. Optional blob/range
anchors resolve locations through the shared backend; see [source regions](source-regions.md).
Git content addresses are not node fingerprints. Impact remains file-level review context,
not proof that every listed node is invalid.

## D. Where to work and what to check

| Change | Verification seam |
| --- | --- |
| Schema, graph, writer, planner or Git | [`tests/`](../tests/): core/Markdown/IDs, transactions/recovery, editor overlays, exact-index and temporal diffs. Read the relevant graph node and ancestors first. |
| Canvas, layout, camera, colors, literal text or drafts | [`graph-ui-common/test/`](../graph-ui-common/test/): model and DOM regressions. Shared real-browser checks live in [`test-host/`](../graph-ui-common/test-host/). |
| Coordination, concurrency or refresh policy | Shared `session`, `documents` and `watch` tests; distinguish per-view queues from project-level document coordination and the filesystem writer lock. |
| VS Code lifecycle or Electron isolation/storage | [`vscode/test/`](../vscode/test/), [`electron/test/`](../electron/test/); optional installed-host suites exercise actual native/desktop behavior. Unit tests are not real-host or cross-platform certification. |

[`graph-ui-common/scripts/build.cjs`](../graph-ui-common/scripts/build.cjs) bundles
pinned Dagre/D3 dependencies and license notices and copies shared runtime sources.
The VS Code and Electron build wrappers add their small adapters. **Edit common
sources, not generated `vscode/media`, `vscode/out` or `electron/build` copies.**
Temporary right-click node labels live only in renderer memory; they do not
enter host state or canonical data. Ordinary focus/camera/draft preferences use
presentation storage. VS Code webview state is scoped per view/project; Electron's
[`PresentationStore`](../electron/store.cjs) uses project-scoped
`graph-presentation.json` in user data. Neither is canonical graph storage.

Serious Git/temporal, application and host integration tests clone the independent
[`gantt.bundle`](../example/gantt/history/gantt.bundle). The tracked `example/gantt`
folder is only a fixture snapshot: Git there finds this development repository.
Use a **new external destination** for manual experiments:

```sh
python example/gantt/history/checkout.py
# Default: ~/Projects/specspec-examples/gantt; existing destinations are refused.
```

Every node-schema change requires reconstructing **all** maintained example
revisions/refs, withdrawn nodes, actual receipts, ledgers and snapshots under the
current schema. Do not add old readers or require obsolete self-specification
history to work. See the [history walkthrough](../example/gantt/history/WALKTHROUGH.md).

From the development Python environment:

```sh
python -m specspec validate --warnings-as-errors
python -m ruff check .
python -m ruff format --check .
python -m pytest
npm --prefix graph-ui-common test
npm --prefix vscode test
npm --prefix electron test
# Optional installed-host checks:
npm --prefix vscode run test:host
npm --prefix electron run test:host
```

To render this diagram locally (the SVG itself has no external dependencies):

```sh
resvg --width 1800 docs/architecture.svg architecture-preview.png
```

### Canonical reasoning behind these boundaries

- [Shared Python backend](../_specspec/LvYBN_4=shared-python-json-backend.md)
  and [shared UI/session](../_specspec/YOPhqYc=shared-ui-and-host-session.md).
- [Managed transactions/recovery](../_specspec/6SyZ-BU=recoverable-workspace-mutations.md)
  versus [native documents](../_specspec/GQdmCrA=native-node-documents-and-independent-graph-views.md).
- [Hash-free synchronization](../_specspec/tvic3PQ=hash-free-schema-and-watcher-reconciliation.md),
  [Git snapshot semantics](../_specspec/Yfy0414=staged-validation-and-semantic-diffs.md),
  and [current-only IDs/schema](../_specspec/qowy5AI=canonical-base64url-and-current-only-backend.md).
- [Independent example workspaces/history](../_specspec/83D9YWw=external-example-checkouts.md).

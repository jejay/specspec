# SpecSpec

Tool-managed Markdown specification graphs, with a compact Python CLI and shared VS Code/Electron graph editor.
[Command guide](docs/cli.md): eight everyday commands, readable defaults, compact JSON and full node-aware diffs.
[Graph structure](docs/graph-structure.md): immediate justifications form a shortcut-free DAG;
node format 7 and API 7 are the current contracts.

New engineers: [architecture guide](docs/architecture.md) and
[owner/agent workflow SVG](docs/architecture.svg).

This repository uses SpecSpec itself: [`_specspec/`](_specspec/) contains its positive current specification, with owner intentions, revisable conclusions and implementation links to actual code/tests. Git retains changed reasoning and execution history. Start with the [graph/process tour](docs/own-spec.md). [`INTENTION_SPEC.md`](INTENTION_SPEC.md) preserves the original owner input; [`CONCLUSION_SPEC.md`](CONCLUSION_SPEC.md) summarizes current technical choices.

## Maintained example: a planning app that changes direction

Gantt is the sole maintained product example. Small generated graphs are focused
test fixtures; `tools/rainbow-playground` is a separate development tool.

[`example/gantt/`](example/gantt/) contains a runnable local planner and a portable
**independent Git history**, with SpecSpec developed before code and two major
redirects withdrawing **13/17** and **9/16** live nodes. The tracked folder is only
a fixture snapshot: Git there finds SpecSpec's development history, so comparisons
of its old-schema commits can fail. Create the real example workspace instead:

```sh
python example/gantt/history/checkout.py
# Default: ~/Projects/specspec-examples/gantt; existing folders are never overwritten.
```

Open that clone in VS Code/Electron and compare `stage/01-code` → `stage/02-spec`
or `stage/02-code` → `stage/03-spec`. Tests/CI use disposable clones of the same
bundle, not your manual workspace or old SpecSpec development commits. See the
[run/history guide](example/gantt/README.md).

Every node-schema change requires rewriting **all maintained example history** as
if it had always used the current SpecSpec version, including every retained ref,
withdrawn node and ledger—not just HEAD. Unrelated development history is untouched;
production tooling remains current-only. The [maintenance procedure](example/gantt/history/WALKTHROUGH.md)
explains the recurring obligation. Plausible graph emergence/revision is enough;
[fictional AI dialogue](example/gantt/STORY.md) is optional illustration, not evidence.

## Implementation source regions

[Source-region guide](docs/source-regions.md): canonical node format 7 supports
whole-file hints and full Git blob anchors with multiple inclusive ranges.
**Strict** (specific) reports internal changes; **expanding** (broad) includes them.
Positions resolve without renumbering the spec; ambiguity/deletion/unavailable
objects remain explicit. Both hosts offer literal source previews and capture
into their existing forms. `sources show/capture/reanchor` and optional
`check --staged --sources` keep writes, staging and object retention deliberate.
No node fingerprints, approval gates or automatic Git writes return.

## Install from this checkout

Python 3.11+ is required. The package is not yet published to PyPI.

```sh
pipx install .
# Or run without a permanent installation:
uvx --from . specspec --help
```

Development:

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest
python -m ruff check .
```

## Explore this repository's graph

After installation, from this repository root:

```sh
specspec check --warnings-as-errors
specspec show
specspec query
specspec query --base HEAD --target workspace
specspec query --human
specspec query --max-distance 2
specspec query --max-distance 50% --influence 25%
specspec query 6EmKDz8= --max-distance 0 --with-ancestors
specspec diff
```

[`query`](docs/query.md) reads a complete revision comparison, defaulting to fresh
HEAD versus saved workspace. Compact rails and full parent headers frame one-line
current body readings, with deleted base records alongside them under their former
parents. Single newlines become spaces; longer runs become ` ¶ `. Types and change
hints use lowercase words without a legend; root content has no extra indent.
Parents always use comma-space separators. Default source items share one
comma-separated `sources: ` line; `--human` preserves logical body lines and lists
sources individually. Both retain one resolved location per reference; edits permitted by strict,
expanding or path-only contracts stay quiet. Broken/uncertain links stay explicit. `--base`/`--target` select versions; `diff` supplies exact text changes.
All selected body content remains present; original layout stays exact in JSON and
node files. Optional `query [ID]` starts a rooted subgraph. Minimum/maximum distance
cutoffs include equality; influence selects highest self-inclusive counts first.
Percentages select a rounded-up share of reachable nodes; multiple criteria return
the union of their independent selections.
`--with-ancestors` completes all matched nodes' parent paths after selection,
without consuming quotas. The example reads the five bindings that justify
left-to-right graph development. Omitted direct children/siblings appear as IDs
only. JSON distinguishes matches from added ancestors; an advanced `--max-bytes`
bounds the exact encoded response and fails rather than truncating.
This self-referencing graph is evolving design documentation: old root revisions
need not work with current tooling. Rigorous Git history checks use the rewritten,
current-schema [Gantt bundle](example/gantt/history/WALKTHROUGH.md), not obsolete
root schemas. Review is a spectrum of confidence: users often spend more attention on early intentions and less on later, revisable conclusions. Once an implementation attempt is worth its uncertainty and token cost, no individual node sign-offs are required. Depth is not a confidence score, and risky details can merit review anywhere. Git additions identify new nodes; implementation and feedback guide further revision. CI checks structural integrity and source references, not whether choices are correct. See [the tour](docs/own-spec.md).

## First graph in another project

This checkout already has a graph: do not run `init` here. In a different project,
supply literal binding text directly as arguments:

```sh
specspec init -m "# Product intention" -m "Help people understand their plan."
specspec show
specspec add --parent <manifesto-id> -m "# Readable timeline" -m "Show the timing clearly."
specspec check
specspec update <requirement-id> -m "# Readable timeline" -m "Show timing and dependencies."
specspec query <requirement-id> --max-distance 0 --with-ancestors
```

`--root <project>` precedes the command when selecting a workspace explicitly.
Repeat `-m/--message` to join literal paragraphs with a blank line; a single argument
preserves its exact text. Use `apply --edits-json '…'` for a whole explicit batch,
including aliases for new nodes without IDs. `update --parent` replaces the entire
parent list. Large input and existing UI transports remain available through
[less-prominent integration inputs](docs/cli.md#integration-only-bulk-inputs).
`delete` removes exactly the named files; surviving conclusions retain their parent
references. Preview with `--dry-run`; use `--yes` for warned noninteractive deletion
of uncommitted selected files. Graph-invalid intermediate edits are saved with
explicit diagnostics. `--require-valid` requires the whole final candidate valid
before writes, and `check` remains strict. The manifesto is protected. There are no
approval statuses, node fingerprints or `--expect` options. See [invalid-state reads,
contextual diffs and batch repair](docs/invalid-graphs.md).

The CLI and graph editor are recommended, but manual `_specspec` Markdown edits are allowed. Validation checks actual schema and graph consistency, not how the files were edited. There are no stored `managed_hash` markers or graph fingerprints. Valid manual changes need no repair or provenance acknowledgement.

Node IDs are canonical padded Base64url of **five random bytes (40 bits)**:
seven symbols plus `=`, eight characters in total. The full trailing equals sign
belongs to the identity. Each filename is exactly `<id>.md`, for example
`XV5_rPQ=.md`, with readable headings inside the document. Tool creation retries project-local
collisions against current node files, including case-only aliases, under the writer
lock. IDs remain case-sensitive; these are references, not security tokens.

The flat `_specspec` directory contains nodes only. Global `format_version` metadata belongs on the manifesto. Runtime locks, staging files, and recovery journals live in the ignored `.specspec-local` directory. Do not delete an unfinished journal: run `specspec recover`. Use `recover --force-lock` only after confirming that no writer is running.

## Schema, deletion and the default HEAD comparison

Canonical node format **7** has no `managed_hash`, `status` or `retired` field. Withdraw a node
by deleting its Markdown file (`specspec delete <id>...` or a valid manual deletion).
Explain why in your normal Git commit. Earlier content stays in Git history, not
flagged files. Managed deletion removes only explicitly selected nodes and warns
about uncommitted selected files before unlinking, including staged changes.
Survivors retain dangling declarations for deliberate reconsideration and repair.
Use `query --issues --with-ancestors` and `diff --with-context` to discover structural
faults and previous/current justification. See [the deletion guide](docs/deletion.md).

The default workspace always compares against **HEAD**, not the index. A deleted
HEAD node remains visible as **D**, with read-only, copyable earlier content and
links, including after staging. It vanishes once the deletion is committed; both
hosts watch HEAD/ref changes. Explicit historical comparisons still show earlier
nodes. Unborn Git has an empty baseline; non-Git/invalid baselines show a clear
comparison-unavailable note. No default polling, staging, commits or status-restore
workflow is introduced. Native-document Delete requires saved project documents.

Only the current compact-ID node format **7** schema and structured API **7** are supported. Obsolete
node formats, UUID IDs and unknown fields are rejected, not silently normalized.
There is no permanent migration command or editor conversion control. Both working
graphs use exact ID-only filenames. Old root-history
comparisons may fail; that is expected and is not a compatibility test obligation.
Upgrade the CLI and extension together. Gantt's maintained standalone history was
rebuilt through current CLI executions and is cloned from its bundle for tests.

## Git

```sh
# Stage your node changes normally, then:
specspec check --staged
specspec diff --json
specspec diff <older-commit> <newer-commit> --json
```

`check --staged` validates **exact staged** node blobs, including partially staged files, without confusing them with unstaged repairs. Configure your own hook framework or manually managed Git hook to call `specspec --root <project> check --staged`, preserving existing commands and executable selection. SpecSpec does not install/replace hooks. Existing hook recipes using old commands need an explicit owner-controlled update.

Comparisons require current-schema graph snapshots. For a compliant historical
corpus, run `python example/gantt/history/checkout.py` and use the independent
clone as described in its walkthrough. Do not run historical comparisons in the
tracked snapshot or reuse obsolete development-repository commit IDs.

Hooks guard against inconsistent graphs, not manual edits, adversarial modification or proof of review. Hooks can be bypassed. Add CI checks for repository-wide protection; keep `.specspec-local/` ignored in the target repository.

## VS Code extension

[Remote SSH/tunnel setup and qualification](docs/remote-workspaces.md) explains workspace-host
installation and real-filesystem boundaries. [Phased loading and diagnostics](docs/loading.md)
describes bounded Git batches, verified derived caches and `specspec.traceLoading`.

```sh
npm --prefix graph-ui-common ci
npm --prefix vscode ci
npm --prefix vscode run compile
```

To try this repository's own graph, open the repository root in VS Code and launch **Run SpecSpec on this repository** (F5). Install the Python package into `.venv` and run `npm --prefix graph-ui-common ci` and `npm --prefix vscode ci` first. The launch compiles the extension, opens `specspec-dev.code-workspace` in a separate development profile, and selects the local Python interpreter explicitly. Trust this repository if VS Code asks, then open a node Markdown file under `_specspec/` or run **SpecSpec: Open Graph** in that development window. The canvas lives in the main editor area, not the sidebar. Node files default to the graph custom editor; **Reopen Editor With → Text Editor** still exposes raw Markdown. Independent tabs and split editors can show different nodes, cameras, and comparisons. There is no Activity Bar container. **Open project** / **SpecSpec: Select Project** can select another graph without reopening the workspace. For Gantt Git comparisons, select the external clone under `~/Projects/specspec-examples/gantt`, not the tracked fixture snapshot. Right-clicking a project folder in Explorer → **SpecSpec: Open Graph** also selects its nearest graph.

The root `.vscode/settings.json` Python Environments discovery list is generated
local state and ignored; it is not the shared interpreter configuration. Tracked
launch/tasks and `specspec-dev.code-workspace` remain the development entry points.

Alternatively, open `vscode/` and launch **Run SpecSpec Extension**. Both launches open the repository's development workspace. If you run **Open Graph** in an empty window, it prompts for a project folder instead of silently returning. Subfolders resolve to the nearest containing `_specspec` project. The **Compare Revisions** command opens an independent panel and accepts a base and optional target commit.

Startup errors appear as notifications and in **View → Output → SpecSpec**. Save/copy any old sidebar form draft before restarting: it is not automatically migrated into new file tabs. After changing the launch setup, stop the old debug session and start F5 again rather than opening the same folder in the old development window.

Configure the CLI invocation in VS Code settings if `specspec` is not on PATH:

```json
{
  "specspec.command": "python",
  "specspec.args": ["-m", "specspec"]
}
```

Use an absolute virtual-environment Python path when necessary. For uvx, configure the command as `uvx` and the argument prefix as `["--from", "/path/to/specspec", "specspec"]`. Explicit CLI settings override the development launch's `SPECSPEC_PYTHON` interpreter.

The editor is a **left-to-right node canvas**. Dagre derives positions from relationships and intrinsic card sizes—not the window dimensions. Ranks develop outward from the manifesto: each node stays in the earliest column permitted by all its parents, rather than being pulled toward shared implementations at the far right. A rank-preserving placement backbone keeps the origin branches vertically compact; every dependency is still drawn and no parent metadata changes. Shorter, label-free compact cards have slightly wider horizontal/vertical gaps for breathing room while retaining a compact overall pitch. Resizing the area clips more or less of the same graph, without wrapping nodes.

Native headlines remain text rather than scaled bitmap overlays. The graph no longer carries a permanent compositor-promotion hint, which visibly improved settled headline sharpness at 250% zoom in the installed Windows VS Code check.

**Node shapes** do not change colors: implementations use completely square 0px corners, requirements rounder 24px corners, and the manifesto is a true circle. Its compact outline is 264×264; its expanded circle grows around the existing native editor rather than clipping fields or reducing the text width.

Curved connections run directly from right to left card boundaries, including circular arcs, without round endpoint dots. They retain a minimum visible stroke thickness when zoomed out. Arrowheads join a smooth, tangent-aligned approach; the line stops at the head base instead of sticking through its tip. Ordinary expanded cards distribute attachments over their height rather than bunching links near the title; manifesto ports span its middle arc to clear thick low-zoom strokes.

**Hover a node** to highlight its immediate incoming and outgoing curves and arrowheads without selecting it. The hovered node and its direct connected neighbors stay undarkened; all other nodes and non-incident connections darken. This also works over expanded form controls, in historical views, and on unsaved draft links. Colored incident connections become brighter and more saturated in their own hue—not washed out toward white—while preserving Git dashes and existing geometry. The emphasis clears when you leave the node.

**Navigate:** middle-button drag or drag the background to pan; wheel / pinch to zoom around the pointer. A rounded floating HUD contains **− / +**, the actual-size percentage and icons for **Frame graph**, contextual **Frame node**, and **Frame rectangle**. Click the rectangle icon or **Ctrl-drag** the canvas (**Command-drag** on Mac), then release the mouse to frame the area. The crosshair and rectangle stay active if the modifier is released during dragging. Escape cancels. With the canvas focused, arrow keys pan, `+` / `-` zoom, `1` restores actual size, and `Home` / `F` frames the graph. Native inputs and Shift highlight gestures retain their behavior. [The canvas tutorial](docs/node-canvas.md#canvas-controls) explains the controls and limits.

At overview altitude, node fills strengthen toward their painted borders over the same 100%-to-12% interval that quiets ordinary arrows. At minimum zoom, nodes read as solid colored shapes; actual-size editing keeps the 15% resting/24% hover tints. The canvas shows concise color legends and leaves tutorial text in documentation.

Click a node to open its **neighborhood view**: compact parents to the left, compact children to the right, and all editing controls inside the expanded selected node. **← Total graph** returns to the overview without discarding a draft; **Resume draft** continues it. **Color by** offers **Min. Distance to Manifesto** (shortest directed path, default), **Max. Distance to Manifesto** (longest directed path), **Absolute influence**, **Relative influence**, **Log Absolute Influence**, **Log Relative Influence**, **Node type**, and **Git/Revision Status**, with legends. Distance modes cycle through the seven colors selected in the playground, from purple (one hop) to red, repeating after seven hops. Node types reuse the selected yellow-green and purple; Added fills take the teal-green closer to the existing added text cue. Paths count relationships from the manifesto in each revision—not the focused subset or comparison overlay. None is an acceptance score. In distance/type/influence modes the manifesto keeps a gray accent and white hover border, with the same tinted background as other cards—not a solid pale fill. In **Git/Revision Status**, including on the manifesto, fills use rainbow green for A, blue for M, red for D, amber for linked-source impact and neutral gray for unchanged nodes. Labels distinguish modification, deletion and source-only impact; no comparison and unsaved drafts are neutral, not fictitious Git changes. Existing themed titles/letters and connection colors remain separate. Status-colored manifesto borders retain their hue on hover like other nodes. All unrelated nodes, including the manifesto, can still darken temporarily.

**Influence** counts self plus unique direct and indirect descendants, with a minimum of one. All four influence modes use a continuous red → yellow → green spectrum (strongest → weakest, no blue). **Absolute influence** normalizes `(influence - 1) / (maximum - 1)`, mapping one to green and the highest non-manifesto count to red. **Relative influence** compares only nodes with the same **maximum** distance to the manifesto, mapping that group's lowest count to green and highest to red. **Log Absolute Influence** and **Log Relative Influence** apply `log(influence)` before normalization in those same domains. This keeps leaf counts defined and emphasizes differences among smaller counts while retaining both linear choices. Tied/singleton groups use green; the manifesto stays gray. Counts and normalization use the full target revision for surviving nodes and full base revision for deleted nodes, even in a focused neighborhood. The continuous legend explains the selected domain; Git accents and spotlight rings remain independent.

To experiment with the distance/type/revision palette yourself, open [`tools/rainbow-playground/index.html`](tools/rainbow-playground/index.html) directly in a browser. Adjust color count, lightness, chroma and hue endpoints; preview dark/light tinted nodes and copy parameters JSON, full palette JSON or CSS variables to paste back to the assistant. This separate offline tool does not apply or save anything in SpecSpec. See its [guide](tools/rainbow-playground/README.md).

**Spotlights:** ask an external agent which nodes express an idea, then add its answer
without an input file: `specspec spotlight add DG-JpDc= rvz48KY= "Spotlight design"`.
Use `--base REV --target REV|workspace` to associate a comparison; the default is
live HEAD → workspace. Explicit Git refs pin commits. The **Spotlights** dropdown
switches to a selected record's comparison, highlights available IDs (including
deleted base nodes) and frames them, retaining drafts. One white ink is controlled
by `--spotlight-color` in `graph-ui-common/media/graph.css`.
**Shift-click node chrome** toggles highlighting; **Ctrl+Shift-click** (macOS:
**Command+Shift-click**) clears one node. **Clear highlight** clears the set.
Manual and spotlight-applied highlights share the same editable set. Use
**Spotlights → Create spotlight from highlights…** to save it with a message;
your agent can then read `specspec spotlight show --json` without copied IDs.
The red badge counts new spotlights since opening, starting at zero on load;
arrivals preserve editing, focus and camera. Metadata-only spotlights persist in
Git-excluded `.specspec-local/annotations/`. Dirty-only workspace checksums warn
about drift while highlighting the best available nodes. Both UIs share the store until
**Flush local spotlights…** or `specspec spotlight flush --yes`.
See [commands, storage and UI semantics](docs/spotlights.md).

Nodes no longer repeat hop-distance labels; the selected color legend explains that context. Child cards still show **N downstream**: the entire reachable descendant subgraph, including every deeper generation, excluding that child and deduplicating shared nodes. Different child totals may overlap; this is potential-impact context rather than guaranteed invalidation.

The webview supports node creation, binding-text/parent/source editing, confirmed physical node deletion, and HEAD-relative graph-diff overlays. **Parents** lists actual linked nodes; a separate **Add parent** picker offers candidates without linking them until you click **Add parent**. The manifesto has no parents or parent-editing controls. Expanded cards are wider so typical 80-column monospace lines fit both the Markdown editor and base-revision text display; compact cards keep their existing size. Node-file tabs update their bound VS Code `TextDocument` through Python-planned edits, with native dirty state, Save/autosave, undo/redo and recovery. Selecting another node opens its file editor. Project panels and Electron retain Python-managed writes; create nodes through **Open Graph**. Commit-target comparison views are read-only. See [document/persistence semantics](docs/native-editors.md). Unsupported schemas report diagnostics without conversion controls; invalid files never silently lose drafts or get rewritten. Untrusted workspaces cannot execute the tool. No project Markdown is executed or loaded as HTML.

**Markdown synchronization:** both hosts reload on file-watcher notifications, coalescing bursts and briefly retrying incomplete saves. Polling is **off by default**. Enable it in VS Code with `"specspec.pollIntervalMs": 5000`, or in Electron with `--poll-interval-ms 5000` / `SPECSPEC_POLL_INTERVAL_MS=5000`; `0` disables it. Watchers remain enabled. Explicit Refresh is always available; watcher-only delivery depends on the OS/filesystem and is not guaranteed on every network/mounted drive.

Native VS Code documents, including unsaved raw Markdown, overlay saved project files for graph and Git context. Split views share document contents, not cameras. Graph-invalid buffers display fresh broken relationships while safe forms remain editable; unreadable targets retain raw repair access and unavailable loads retain marked last-usable context. Native Save can persist invalid text, so validate before committing. Unapplied form input has a separate recovery backup, not a second silently diverging document. Project CLI actions refuse dirty open SpecSpec documents. Managed project/Electron forms retain drafts, caret, camera and original records; same-node external changes ask before overwriting, and deleted drafts remain copyable. Invalid external files are never repaired automatically. Native text saves are **not** Python-journaled transactions; CLI/Electron writes still use locks, original-byte checks and recovery.

Layout and navigation reuse locally bundled Dagre and D3 libraries, not a Blender engine port or a remote renderer. `npm run compile` builds the offline browser bundle and its license notices. See [the library rationale](docs/node-canvas.md).

Run `npm --prefix graph-ui-common test` for the shared renderer/session/camera/layout and `npm --prefix vscode test` for bridge, project-selection, and activation regression tests. `npm --prefix vscode run test:host` additionally opens the installed VS Code in a disposable test profile and checks workspace loading, a real DOM-render acknowledgement, minimum/maximum path colors and label removal, shorter-card fit, high-zoom headline rendering, earliest manifesto-anchored ranks, minimum-zoom stroke/head visibility, circle-free arrow joins, left-to-right flow, viewport-size invariance, cursor-anchored wheel zoom, drag panning, focus/back cameras, native form gestures, color modes, root controls, immutable CLI spotlight arrivals/list integration, session-only count badges, white identity-based inset-ring paint, zoom-dependent ordinary-arrow darkening, painted-stroke/content clearance, and resized side-boundary endpoints. The installed-host test also opens canonical files through the default custom editor and checks native dirty/save/undo/redo, raw edits, invalid-buffer repair, shared split documents and independent cameras on a compact nested graph. This is not large-graph typing-performance evidence. The host-test runner requires Node 22+ and opens a loopback-only debugger on a disposable profile. Set `VSCODE_EXECUTABLE` or `SPECSPEC_PYTHON` if installation paths differ. Only that isolated automated test disables workspace trust; normal development launches retain it. To save screenshots, set `SPECSPEC_SCREENSHOT_DIR` to an output directory when running the host test. Full manual mutation/review and revision-picker interaction checks remain follow-up work.

## Standalone desktop and shared UI

[`graph-ui-common/`](graph-ui-common/) is the single renderer/template/camera/model and
guarded host-session source. VS Code and the initial [Electron adapter](electron/README.md)
build the same offline assets. No React rewrite, renderer fork, or duplicate canonical
mutation engine is introduced. Drafts/cameras are scoped per project and, in VS Code, per view. Native file edits
use host text documents; managed project/Electron forms retain original node
contents alongside each draft, without hashes. Both use the same Python graph rules,
not necessarily the same host persistence lifecycle.

```sh
npm --prefix graph-ui-common ci
npm --prefix electron ci
# Windows; use ../.venv/bin/python on Linux:
npm --prefix electron start -- --python ../.venv/Scripts/python.exe --project ..
```

Without `--project`, choose **Open project** and explicitly **Trust and Open**. Python/Git
are external prerequisites. The isolated/sandboxed desktop renderer has no Node/FS/spawn
API, and the app blocks remote requests, navigation and popups. The portable package
command and Linux/Windows CI checks are documented in `electron/README.md`; Linux execution,
remote CI, installers/signing and Claude Code/Codex connectors are **not claimed completed**.
The adapter seam supports later integration work, not an existing agent integration.

**Git cues:** node titles and bottom-right **A/M/D** share themed
colors, relative to the selected base. A/D use VS Code Git resource foregrounds; M uses
the theme's modified-gutter blue, since modified-resource foreground is often amber.
Electron uses Dark Modern/default Git colors. Larger, heavier corner letters fit within unchanged compact cards. Semantic fills, source-only impact and
deletion stay separate: source changes don't invent M, and D is physical deletion relative to the comparison base.
The [selected Spectrum flow identity](branding/README.md) supplies the optical header
symbol and launcher tile. The symbol sits directly before revision context; Refresh
is an icon. VS Code project selection remains in its command palette, while Electron
also keeps Open project in its header and Project menu. **Ctrl+S** (**Command+S** on
macOS) saves the focused node form through its existing native or managed save path.

## Current scope

This is an initial implementation, not a production-ready release. Transactions recover from process interruptions; full power-loss durability and adversarial filesystem race protection are not guaranteed. Graph rendering uses Dagre's deterministic layered arrangement and a separate D3 camera; large graphs are not virtualized. Source symbols are descriptive, not language-resolved. Choice groups, large-graph UI optimization, and publishing remain follow-up work. Per-node approval enforcement and review-receipt gates are not part of the current direction. The self-hosted graph separates user intentions from revisable conclusions through explanations and relationships; implementation records describe actual verification and remaining limitations.

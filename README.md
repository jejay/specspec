# SpecSpec

Tool-managed Markdown specification graphs, with a Python CLI and a VS Code graph editor.

This repository uses SpecSpec itself: [`_specspec/`](_specspec/) contains its working specification, with core intentions, revisable technical choices, withdrawn design history, and implementation links to actual code/tests. Start with the [graph tour](docs/own-spec.md). [`INTENTION_SPEC.md`](INTENTION_SPEC.md) and [`CONCLUSION_SPEC.md`](CONCLUSION_SPEC.md) remain the original intention/design context.

## Worked example: a planning app that changes direction

[`example/gantt/`](example/gantt/) is a runnable local Gantt planner developed with
SpecSpec **before the first code**, plus a clearly [simulated user/AI conversation](example/gantt/STORY.md).
Two major redirects withdraw **13/17** and **9/16** live graph nodes, with original
reasoning and runnable prototypes retained in real Git stage commits. The final app
has weekday dependency forecasts, an explicit what-if baseline, native forms, and
safe local JSON import/export. See the [run/history guide](example/gantt/README.md).
It has its own `_specspec/` graph—not a nested Git repository or an approval workflow.

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
specspec validate --warnings-as-errors
specspec list --json
specspec context qowy5AI= --json
specspec export --format mermaid
```

The context example follows the current compact-ID conclusion back to its intentions.
This self-referencing graph is evolving design documentation: old root revisions
need not work with current tooling. Rigorous Git history checks use the rewritten,
current-schema [Gantt bundle](example/gantt/history/WALKTHROUGH.md), not obsolete
root schemas. Review is a spectrum of confidence: users often spend more attention on early intentions and less on later, revisable conclusions. Once an implementation attempt is worth its uncertainty and token cost, no individual node sign-offs are required. Depth is not a confidence score, and risky details can merit review anywhere. Git additions identify new nodes; implementation and feedback guide further revision. CI checks structural integrity and source references, not whether choices are correct. See [the tour](docs/own-spec.md).

## First graph in another project

This checkout already has a graph: do not run `init` here. In a different project, write manifesto **body text** in a file outside `_specspec`, then:

```sh
specspec init --manifesto manifesto.md
specspec list --json
specspec add --parent <manifesto-id> --slug validate-edits --body requirement.md
specspec validate
specspec update <requirement-id> --body revised-requirement.md
specspec context <requirement-id> --json
```

`--root <project>` precedes the command when selecting a workspace explicitly. Body input accepts `-` for stdin. `update --parent` replaces the entire parent list. `retire` and `restore` take multiple explicitly named IDs; withdrawal dependency rules apply to the resulting batch. There is no approval status or `accept` command. Mutations support `--json`; there are no fingerprints or `--expect` options.

The CLI and graph editor are recommended, but manual `_specspec` Markdown edits are allowed. Validation checks actual schema and graph consistency, not how the files were edited. There are no stored `managed_hash` markers or graph fingerprints. Valid manual changes need no repair or provenance acknowledgement.

Node IDs are canonical padded Base64url of **five random bytes (40 bits)**:
seven symbols plus `=`, eight characters in total. The full trailing equals sign
belongs to the identity and also separates it from the filename summary, for
example `XV5_rPQ=specspec-manifesto.md`. Tool creation retries project-local
collisions, including withdrawn nodes and case-only aliases, under the writer
lock. IDs remain case-sensitive; these are references, not security tokens.

The flat `_specspec` directory contains nodes only. Global `format_version` metadata belongs on the manifesto. Runtime locks, staging files, and recovery journals live in the ignored `.specspec-local` directory. Do not delete an unfinished journal: run `specspec recover`. Use `recover --force-lock` only after confirming that no writer is running.

## Schema and withdrawal

Format 3 has no `managed_hash` or `status` field. Ordinary nodes have no stored review stage; optional `retired: true` marks a withdrawn explanation retained as history. The manifesto cannot be retired, and live nodes cannot depend on retired parents. `specspec restore ID` reverses withdrawal; it does not declare approval.

Only the current compact-ID format/API **3** schema is supported. Obsolete
node formats, UUID IDs and unknown fields are rejected, not silently normalized.
There is no permanent migration command or editor conversion control. Both working
graphs were converted once through a temporary journaled tool. Old root-history
comparisons may fail; that is expected and is not a compatibility test obligation.
Upgrade the CLI and extension together. Gantt's maintained standalone history was
rebuilt through current CLI executions and is cloned from its bundle for tests.

## Git

```sh
specspec hook install
# Stage your node changes normally, then:
specspec hook check
specspec diff --base HEAD --json
specspec diff --base <older-commit> --target <newer-commit> --json
```

The pre-commit hook validates the **staged** node blobs, including schema and graph relationships. It does not confuse unstaged edits with the contents being committed. Installation refuses existing hooks and respects `core.hooksPath`; chain `specspec --root <project> hook check` manually when another hook already exists. The installed hook uses the Python environment from installation, which must remain available; reinstall it after moving environments.

Comparisons require current-schema graph snapshots. For a compliant historical
corpus, clone `example/gantt/history/gantt.bundle` as described in its walkthrough.

Hooks guard against inconsistent graphs, not manual edits, adversarial modification, or proof of review. Hooks can be bypassed. Add CI validation for repository-wide protection. Installing a hook does not stage files, commit changes, or modify project ignore rules; keep `.specspec-local/` ignored in the target repository.

## VS Code extension

```sh
npm --prefix graph-ui-common ci
npm --prefix vscode ci
npm --prefix vscode run compile
```

To try this repository's own graph, open the repository root in VS Code and launch **Run SpecSpec on this repository** (F5). Install the Python package into `.venv` and run `npm --prefix graph-ui-common ci` and `npm --prefix vscode ci` first. The launch compiles the extension, opens `specspec-dev.code-workspace` in a separate development profile, and selects the local Python interpreter explicitly. Trust this repository if VS Code asks, then open a node Markdown file under `_specspec/` or run **SpecSpec: Open Graph** in that development window. The canvas lives in the main editor area, not the sidebar. Node files default to the graph custom editor; **Reopen Editor With → Text Editor** still exposes raw Markdown. Independent tabs and split editors can show different nodes, cameras, and comparisons. There is no Activity Bar container. **Open project** / **SpecSpec: Select Project** can select a nested graph such as `example/gantt` without reopening the workspace. Right-clicking a project folder in Explorer → **SpecSpec: Open Graph** also selects its nearest graph.

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

Curved connections run directly from right to left card boundaries, without round endpoint dots. They retain a minimum visible stroke thickness when zoomed out. Arrowheads join a smooth, tangent-aligned approach; the line stops at the head base instead of sticking through its tip. Expanded cards distribute attachments over their height rather than bunching links near the title.

**Hover a node** to highlight its immediate incoming and outgoing curves and arrowheads without selecting it. The hovered node and its direct connected neighbors stay undarkened; all other nodes and non-incident connections darken. This also works over expanded form controls, in historical views, and on unsaved draft links. Colored incident connections become brighter and more saturated in their own hue—not washed out toward white—while preserving Git dashes and existing geometry. The emphasis clears when you leave the node.

**Navigate:** middle-button drag or drag the background to pan; wheel / pinch to zoom around the pointer. Use **− / +**, **100%**, **Frame graph** and **Frame node** to recover your view. With the canvas focused, arrow keys pan, `+` / `-` zoom, `1` restores actual size, and `Home` / `F` frames the graph. Native form scrolling, text selection, and editing retain their normal behavior. Cameras survive refresh and back navigation; no positions or camera preferences are written into `_specspec`.

Click a node to open its **neighborhood view**: compact parents to the left, compact children to the right, and all editing controls inside the expanded selected node. **← Total graph** returns to the overview without discarding a draft; **Resume draft** continues it. **Color by** offers **Min. Distance to Manifesto** (shortest directed path, default), **Max. Distance to Manifesto** (longest directed path), **Node type**, and **Git/Revision Status**, with legends. Distance modes cycle through nine distinct, gently colored rainbow steps from violet (one hop) to red, repeating after nine hops, with slightly increased saturation. Node types reuse the table's teal and violet. Paths count relationships from the manifesto in each revision—not the focused subset or comparison overlay. None is an acceptance score. In distance/type modes the manifesto keeps a gray accent and white hover border, with the same tinted background as other cards—not a solid pale fill. In **Git/Revision Status**, including on the manifesto, fills use rainbow green for A, blue for M/R, red for D, amber for linked-source impact and neutral gray for unchanged nodes. Labels distinguish rename/source-only/withdrawal; no comparison and unsaved drafts are neutral, not fictitious Git changes. Existing themed titles/letters and connection colors remain separate. Status-colored manifesto borders retain their hue on hover like other nodes. All unrelated nodes, including the manifesto, can still darken temporarily.

To experiment with the palette yourself, open [`tools/rainbow-playground/index.html`](tools/rainbow-playground/index.html) directly in a browser. Adjust color count, lightness, chroma and hue endpoints; preview dark/light tinted nodes and copy parameters JSON, full palette JSON or CSS variables to paste back to the assistant. This separate offline tool does not apply or save anything in SpecSpec. See its [guide](tools/rainbow-playground/README.md).

Nodes no longer repeat hop-distance labels; the selected color legend explains that context. Child cards still show **N downstream**: the entire reachable descendant subgraph, including every deeper generation, excluding that child and deduplicating shared nodes. Different child totals may overlap; this is potential-impact context rather than guaranteed invalidation.

The webview supports node creation, binding-text/parent/source editing, explicit withdrawal/restoration, and graph-diff overlays. **Parents** lists actual linked nodes; a separate **Add parent** picker offers candidates without linking them until you click **Add parent**. The manifesto has no parents or parent-editing controls. Expanded cards are wider so typical 80-column monospace lines fit both the Markdown editor and base-revision text display; compact cards keep their existing size. Node-file tabs update their bound VS Code `TextDocument` through Python-planned edits, with native dirty state, Save/autosave, undo/redo and recovery. Selecting another node opens its file editor. Project panels and Electron retain Python-managed writes; create nodes through **Open Graph**. Commit-target comparison views are read-only. See [document/persistence semantics](docs/native-editors.md). Unsupported schemas report diagnostics without conversion controls; invalid files never silently lose drafts or get rewritten. Untrusted workspaces cannot execute the tool. No project Markdown is executed or loaded as HTML.

**Markdown synchronization:** both hosts reload on file-watcher notifications, coalescing bursts and briefly retrying incomplete saves. Polling is **off by default**. Enable it in VS Code with `"specspec.pollIntervalMs": 5000`, or in Electron with `--poll-interval-ms 5000` / `SPECSPEC_POLL_INTERVAL_MS=5000`; `0` disables it. Watchers remain enabled. Explicit Refresh is always available; watcher-only delivery depends on the OS/filesystem and is not guaranteed on every network/mounted drive.

Native VS Code documents, including unsaved raw Markdown, overlay saved project files for graph and Git context. Split views share document contents, not cameras. Invalid buffers keep the last valid graph marked out of date while the bound form remains editable for repair; native Save can persist invalid text, so validate before committing. Unapplied form input has a separate recovery backup, not a second silently diverging document. Project CLI actions refuse dirty open SpecSpec documents. Managed project/Electron forms retain drafts, caret, camera and original records; same-node external changes ask before overwriting, and deleted drafts remain copyable. Invalid external files are never repaired automatically. Native text saves are **not** Python-journaled transactions; CLI/Electron writes still use locks, original-byte checks and recovery.

Layout and navigation reuse locally bundled Dagre and D3 libraries, not a Blender engine port or a remote renderer. `npm run compile` builds the offline browser bundle and its license notices. See [the library rationale](docs/node-canvas.md).

Run `npm --prefix graph-ui-common test` for the shared renderer/session/camera/layout and `npm --prefix vscode test` for bridge, project-selection, and activation regression tests. `npm --prefix vscode run test:host` additionally opens the installed VS Code in a disposable test profile and checks workspace loading, a real DOM-render acknowledgement, minimum/maximum path colors and label removal, shorter-card fit, high-zoom headline rendering, earliest manifesto-anchored ranks, minimum-zoom stroke/head visibility, circle-free arrow joins, left-to-right flow, viewport-size invariance, cursor-anchored wheel zoom, drag panning, focus/back cameras, native form gestures, color modes, root controls, painted-stroke/content clearance, and resized side-boundary endpoints. The installed-host test also opens canonical files through the default custom editor and checks native dirty/save/undo/redo, raw edits, invalid-buffer repair, shared split documents and independent cameras on a compact nested graph. This is not large-graph typing-performance evidence. The host-test runner requires Node 22+ and opens a loopback-only debugger on a disposable profile. Set `VSCODE_EXECUTABLE` or `SPECSPEC_PYTHON` if installation paths differ. Only that isolated automated test disables workspace trust; normal development launches retain it. To save screenshots, set `SPECSPEC_SCREENSHOT_DIR` to an output directory when running the host test. Full manual mutation/review and revision-picker interaction checks remain follow-up work.

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

**Git cues:** node titles and bottom-right **A/M/D** (plus **R** for rename) share themed
colors, relative to the selected base. A/D use VS Code Git resource foregrounds; M uses
the theme's modified-gutter blue, since modified-resource foreground is often amber.
Electron uses Dark Modern/default Git colors. Larger, heavier corner letters fit within unchanged compact cards. Semantic fills, source-only impact and
withdrawal stay separate: source changes don't invent M, and retirement is not deletion.
The [full dachshund SVG and minimal icon](branding/README.md) are preserved/derived
separately; resvg miniature light/dark renders and real-host screenshots were inspected.

## Current scope

This is an initial implementation, not a production-ready release. Transactions recover from process interruptions; full power-loss durability and adversarial filesystem race protection are not guaranteed. Graph rendering uses Dagre's deterministic layered arrangement and a separate D3 camera; large graphs are not virtualized. Source symbols are descriptive, not language-resolved. Choice groups, large-graph UI optimization, and publishing remain follow-up work. Per-node approval enforcement and review-receipt gates are not part of the current direction. The self-hosted graph separates user intentions from revisable conclusions through explanations and relationships; implementation records describe actual verification and remaining limitations.

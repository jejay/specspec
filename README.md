# SpecSpec

Tool-managed Markdown specification graphs, with a Python CLI and a VS Code graph editor.

This repository uses SpecSpec itself: [`_specspec/`](_specspec/) contains its working specification, with core intentions, revisable technical choices, withdrawn design history, and implementation links to actual code/tests. Start with the [graph tour](docs/own-spec.md). [`INTENTION_SPEC.md`](INTENTION_SPEC.md) and [`CONCLUSION_SPEC.md`](CONCLUSION_SPEC.md) remain the original intention/design context.

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
specspec context cc058342-0f01-4dc1-99bc-439b445c5a04 --json
specspec diff --base HEAD --json
```

The context example follows the actual Git implementation back to its requirements. Review is a spectrum of confidence: users often spend more attention on early intentions and less on later, revisable conclusions. Once an implementation attempt is worth its uncertainty and token cost, no individual node sign-offs are required. Depth is not a confidence score, and risky details can merit review anywhere. Git additions identify new nodes; implementation and feedback guide further revision. CI checks structural integrity and source references, not whether choices are correct. See [the tour](docs/own-spec.md).

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

`--root <project>` precedes the command when selecting a workspace explicitly. Body input accepts `-` for stdin. `update --parent` replaces the entire parent list. `retire` and `restore` take multiple explicitly named IDs; withdrawal dependency rules apply to the resulting batch. There is no approval status or `accept` command. Mutations support `--expect <fingerprint>` and `--json`.

Do not edit `_specspec` files directly. The CLI validates the candidate graph and maintains integrity hashes. Read commands never refresh these hashes. An unmanaged body/metadata edit causes validation failure; restore the file from Git or undo the edit and apply it through `update`.

The flat `_specspec` directory contains nodes only. Global `format_version` metadata belongs on the manifesto. Runtime locks, staging files, and recovery journals live in the ignored `.specspec-local` directory. Do not delete an unfinished journal: run `specspec recover`. Use `recover --force-lock` only after confirming that no writer is running.

## Schema and withdrawal

Format 2 has no `status` field. Ordinary nodes have no stored review stage; optional `retired: true` marks a withdrawn explanation retained as history. The manifesto cannot be retired, and live nodes cannot depend on retired parents. `specspec restore ID` reverses withdrawal; it does not declare approval.

Version-one graphs and old Git revisions remain readable. The reader verifies the original hashes, maps legacy retirement to withdrawal, and does not expose proposed/accepted labels. Convert an older workspace explicitly before editing:

```sh
specspec list --json
specspec migrate --expect <displayed-fingerprint> --json
specspec list --live --json
specspec list --retired --json
```

Migration journals the complete conversion, preserves IDs, paths, body bytes, dependencies, references, extensions, and unaffected comments, and refuses stale or unmanaged input. An interrupted conversion uses the normal `recover` workflow. Repeating migration is a no-op. The shared JSON API is now **version 2**; upgrade the CLI and extension together.

## Git

```sh
specspec hook install
# Stage your node changes normally, then:
specspec hook check
specspec diff --base HEAD --json
specspec diff --base <older-commit> --target <newer-commit> --json
```

The pre-commit hook validates the **staged** node blobs, including integrity and graph relationships. It does not confuse unstaged edits with the contents being committed. Installation refuses existing hooks and respects `core.hooksPath`; chain `specspec --root <project> hook check` manually when another hook already exists. The installed hook uses the Python environment from installation, which must remain available; reinstall it after moving environments.

Hooks and integrity hashes guard against accidents, not adversarial modification or proof of review. Hooks can be bypassed. Add CI validation for repository-wide protection. Installing a hook does not stage files, commit changes, or modify project ignore rules; keep `.specspec-local/` ignored in the target repository.

## VS Code extension

```sh
npm --prefix vscode ci
npm --prefix vscode run compile
```

To try this repository's own graph, open the repository root in VS Code and launch **Run SpecSpec on this repository** (F5). Install the Python package into `.venv` and run `npm --prefix vscode ci` first. The launch compiles the extension, opens `specspec-dev.code-workspace` in a separate development profile, and selects the local Python interpreter explicitly. Trust this repository if VS Code asks, then run **SpecSpec: Open Graph** in that development window.

Alternatively, open `vscode/` and launch **Run SpecSpec Extension**. Both launches open the repository's development workspace. If you run **Open Graph** in an empty window, it prompts for a project folder instead of silently returning. Subfolders resolve to the nearest containing `_specspec` project. The **Compare Revisions** command accepts a base and optional target commit.

Startup errors appear as notifications and in **View → Output → SpecSpec**. After changing the launch setup, stop the old debug session and start F5 again rather than opening the same folder in the old development window.

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

**Hover a node** to highlight its immediate incoming and outgoing curves and arrowheads without selecting it. This also works over expanded form controls, in historical views, and on unsaved draft links. The temporary emphasis preserves Git hues/dashes and existing geometry, and clears when you leave the node.

**Navigate:** middle-button drag or drag the background to pan; wheel / pinch to zoom around the pointer. Use **− / +**, **100%**, **Frame graph** and **Frame node** to recover your view. With the canvas focused, arrow keys pan, `+` / `-` zoom, `1` restores actual size, and `Home` / `F` frames the graph. Native form scrolling, text selection, and editing retain their normal behavior. Cameras survive refresh and back navigation; no positions or camera preferences are written into `_specspec`.

Click a node to open its **neighborhood view**: compact parents to the left, compact children to the right, and all editing controls inside the expanded selected node. **← Total graph** returns to the overview without discarding a draft; **Resume draft** continues it. **Color by** offers **Min. Distance to Manifesto** (shortest directed path, default), **Max. Distance to Manifesto** (longest directed path), and existing node types, with a legend. Paths count relationships from the manifesto in each revision—not the focused subset or comparison overlay. None is an acceptance score.

Nodes no longer repeat hop-distance labels; the selected color legend explains that context. Child cards still show **N downstream**: the entire reachable descendant subgraph, including every deeper generation, excluding that child and deduplicating shared nodes. Different child totals may overlap; this is potential-impact context rather than guaranteed invalidation.

The webview supports node creation, binding-text/parent/source editing, explicit withdrawal/restoration, and graph-diff overlays. **Parents** lists actual linked nodes; a separate **Add parent** picker offers candidates without linking them until you click **Add parent**. The manifesto has no parents or parent-editing controls. It uses the Python CLI for all writes. Historical comparison views are read-only. Legacy workspaces offer **Migrate specification** before editing; dirty drafts must be discarded first and never silently acquire a newer fingerprint. Untrusted workspaces cannot execute the tool. No project Markdown is executed or loaded as HTML.

Layout and navigation reuse locally bundled Dagre and D3 libraries, not a Blender engine port or a remote renderer. `npm run compile` builds the offline browser bundle and its license notices. See [the library rationale](docs/node-canvas.md).

Run `npm --prefix vscode test` for bridge, renderer, camera/layout, project-selection, and activation regression tests. `npm --prefix vscode run test:host` additionally opens the installed VS Code in a disposable test profile and checks workspace loading, a real DOM-render acknowledgement, minimum/maximum path colors and label removal, shorter-card fit, high-zoom headline rendering, earliest manifesto-anchored ranks, minimum-zoom stroke/head visibility, circle-free arrow joins, left-to-right flow, viewport-size invariance, cursor-anchored wheel zoom, drag panning, focus/back cameras, native form gestures, color modes, root controls, painted-stroke/content clearance, and resized side-boundary endpoints. The host-test runner requires Node 22+ and opens a loopback-only debugger on a disposable profile. Set `VSCODE_EXECUTABLE` or `SPECSPEC_PYTHON` if installation paths differ. Only that isolated automated test disables workspace trust; normal development launches retain it. To save screenshots, set `SPECSPEC_SCREENSHOT_DIR` to an output directory when running the host test. Full manual mutation/review and revision-picker interaction checks remain follow-up work.

## Current scope

This is an initial implementation, not a production-ready release. Transactions recover from process interruptions; full power-loss durability and adversarial filesystem race protection are not guaranteed. Graph rendering uses Dagre's deterministic layered arrangement and a separate D3 camera; large graphs are not virtualized. Source symbols are descriptive, not language-resolved. Choice groups, large-graph UI optimization, and publishing remain follow-up work. Per-node approval enforcement and review-receipt gates are not part of the current direction. The self-hosted graph separates user intentions from revisable conclusions through explanations and relationships; implementation records describe actual verification and remaining limitations.

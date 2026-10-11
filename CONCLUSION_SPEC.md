# Conclusion Specification: Technical Proposal

The working proposal nodes and implementation mappings now live in [`_specspec/`](_specspec/). See the [repository graph tour](docs/own-spec.md) for the user's risk-proportionate review principle, current choices, and withdrawn history. This document is design context, not an individual sign-off workflow.

## 1. Package and architecture

Build a Python 3.11+ package with a `specspec` console entry point, a reusable library, and a separate TypeScript VS Code extension. Use Hatchling for packaging, Click for the CLI, `ruamel.yaml` for round-trip frontmatter, and pytest for tests.

```text
src/specspec/
  model.py        # Strict node schema, diagnostics, normalized records
  format.py       # Frontmatter parsing and targeted serialization
  graph.py        # Structural checks, traversal, deterministic ordering
  workspace.py    # Discovery, snapshots, managed mutations, recovery
  git.py          # Index/revision snapshots, semantic diff, hook installation
  cli.py          # Commands and versioned JSON responses
graph-ui-common/
  media/          # Single native renderer, camera/model/CSS source
  host/           # Shared guarded session, CLI bridge and project discovery
  view.cjs        # Shared nonce-protected local template
vscode/
  src/            # Native node editors/project panels, dialogs/trust/watchers
  media/          # Generated shared assets + tiny host adapter
electron/
  main.cjs        # Authorized local shell, bounded IPC/CLI and asset protocol
  preload.cjs     # Narrow context-isolated/sandboxed renderer port
branding/
  dachshund.svg    # Exact supplied brand import
  activity-icon.svg # Minimal themed 24x24 mask
```

The [portable-host revision](docs/platforms.md) shares the existing native canvas and
serialized graph session rather than introducing renderer forks. VS Code hosts it
in native node-file custom text editors and independent project/comparison panels;
there is no Activity Bar container. Electron targets Windows and Linux with
external Python/Git. Its restricted renderer cannot select executables
or read project files. Later Claude Code/Codex transports remain undecided work.
The preceding Activity Bar host choice is withdrawn, not retained as a runtime
compatibility mode. Native saves use non-writing Python plans and VS Code documents;
managed project/Electron operations retain the Python writer. The dachshund artwork and tiny monochrome derivative remain separate.
Git title/corner A/M/D/R colors use theme tokens, with modified-gutter blue for M;
semantic fills, source-only context and withdrawal remain independent.

The adapters invoke the CLI with argument arrays and JSON output. It contains no independent schema, withdrawal, or graph validation implementation. The Python library does not depend on VS Code or Git for ordinary workspace operations.

Distribution targets are `pipx install specspec` and `uvx --from specspec specspec`. Until published, support installation from a local checkout or Git URL. Do not assume the PyPI name is available; confirm it before publishing.

## 2. Files and schema

```text
_specspec/
  XV5_rPQ=project-manifesto.md
  Zm9vYmE=validate-graph-edits.md
  ZnJlc2g=validator-implementation.md
```

Use canonical padded RFC 4648 Base64url IDs over `secrets.token_bytes(5)`:
40 random bits encoded as seven symbols plus one `=`, for eight characters total.
Keep the trailing equals sign in the full identity and use it as the sole filename
separator: `<id><ascii-slug>.md`. Generate under the writer lock and retry exact
or case-only collisions against all current nodes, including withdrawn nodes,
regardless of summary. Validate zero pad bits and reject case-only graph aliases
for portable filename safety. Frontmatter is authoritative, with a matching filename. Resolve references only by full ID. Discover direct files only; reject directories, symlinks, and non-node files.

Search upward for the nearest `_specspec` directory, stopping even when it is invalid. Support an explicit project-root override. Keep all operation state outside `_specspec`; do not introduce a configuration file or node subdirectory.

Current format/API 3 frontmatter (the sole supported scheme):

| Field | Rule |
| --- | --- |
| `id` | Required canonical padded Base64url of five octets, including `=`. |
| `type` | `manifesto`, `requirement`, or `implementation`. |
| `retired` | Optional strict boolean; true means withdrawn, not unreviewed. No approval `status` field. |
| `parents` | Required array of unique IDs; order is non-semantic. |
| `format_version` | Required integer `3` on the manifesto only. |
| `sources` | Optional implementation-only `{path, symbol?}` entries. |
| `extensions` | Optional namespaced JSON-compatible metadata mapping. |

Store incoming relationships in `parents`, avoiding writes to parent files when a child is added. Require requirement parents for implementations as part of the rooted node grammar.

Bootstrap parsing locates the unique manifesto and its version before full schema validation. Missing, ambiguous, or unsupported versions fail explicitly. Reject duplicate YAML keys, explicit tags, anchors/aliases, unknown fields, coercion, invalid UTF-8, and files larger than 1 MiB.

Use strict Python dataclasses and explicit validators initially. Retain the YAML syntax tree and the original body for targeted updates. Updating metadata must preserve body bytes; editing the body must preserve unaffected frontmatter comments. Tool-controlled fields and filenames may be normalized on writes.

Allow lists and headings without interpreting them as separate graph elements. Split items when independent review or reuse warrants separate IDs, not according to sentence or list counts.

## 3. Graph engine

Maintain node, parent, and child dictionaries. Validate file schemas and duplicate IDs before resolving edges; never silently discard malformed nodes to manufacture a usable graph.

Use deterministic Kahn ordering and iterative traversal. Return a concrete cycle witness rather than only reporting that sorting failed. Apply structural checks to every node and withdrawal checks to the live graph; there are no parent-approval gates. Invalid snapshots still expose diagnostics and file-level records, but cannot drive editing or complete context queries.

Calculate closures on demand and rebuild from files on every invocation initially. The core graph checks are linear; deterministic heap ordering adds `O(V log V)`. A daemon or persisted index is unnecessary until measured latency justifies one.

## 4. Tool-driven edits and permitted manual changes

The user's later consenting-adults correction removes `managed_hash`, graph
fingerprints, `--expect` and hash verification. CLI/UI edits remain recommended;
manual Markdown changes are permitted and validated on schema/graph consistency,
not provenance. API/format 3 contains no replacement marker or fingerprint.
Superseded node schemes and unknown metadata fail validation; no obsolete reader
or normalization path remains. Git compares semantic records and raw bytes directly.
Require valid input/candidate graphs for tool mutations; no special repair or
acknowledgement workflow is required merely because an edit was manual.

### Transaction strategy

Use `.specspec-local/` at the project root for a lock, staged replacement files, and a recovery journal; ignore it in Git. Reject symlinked state directories and verify same-filesystem staging before replacement.

Under the lock, load and validate the workspace, construct the candidate graph and validate the result without snapshot hashes. Journal original and replacement bytes before touching canonical files. Compare original file bytes directly immediately before applying replacements and validate afterwards.

Batch replacement is not filesystem-atomic. Interrupted operations remain explicit and block further mutations. Provide `recover` to restore original files only if each current file matches a known original or replacement state. Refuse to overwrite intervening external edits. Detect unclean locks and incomplete journals on reads; do not discard recovery data as cache.

`init` stages an entire new directory before exposing it at `_specspec`, refuses an existing workspace, and obtains manifesto text from the caller rather than inventing it.

## 5. Risk-proportionate review and withdrawal

Review is a spectrum of confidence and attention, often concentrated on early intentions near the manifesto rather than every later conclusion. This is not a deterministic depth rule: risky details may warrant substantial review anywhere. Once the user judges an implementation attempt worth its uncertainty and token cost, no per-node proposed/accepted ceremony blocks it. Keep conclusions independently revisable as implementation and feedback improve understanding; neither implementation nor a commit proves correctness.

Remove approval statuses, scores, parent-approval rules, and the accept command. Git additions communicate newness relative to the chosen revision; semantic changes and linked-source impact provide review context. Context export lists live siblings without deciding whether they are competing alternatives.

Keep a strict optional retired boolean for withdrawal and retained history. Explicit retire/restore batches name their nodes; live nodes cannot depend on withdrawn parents, and the manifesto cannot be withdrawn. Restoration does not claim review or approval. Keep withdrawal controls separate from content saves.

Keep only the current node scheme in production tooling. The authorized conversion
of both working graphs was performed once through a temporary journaled tool, not
a shipped migration command. The self-referencing root graph's older revisions
need not work with the current reader. Test Git tooling against the independent
rewritten Gantt history, stored as a bundle with freshly executed current CLI
receipts and real stage commit IDs. No unrelated SpecSpec history is rewritten.
See the current-only intention and separate backend/history conclusions in the graph.

Explicit choice groups remain separate work; the earlier approval-receipt candidate is withdrawn, not a required future workflow.

## 6. CLI and machine interface

```text
specspec [--root <project>] init --manifesto <file>
specspec [--root <project>] validate [--json] [--warnings-as-errors]
specspec [--root <project>] add --type requirement --parent <id> --slug <text> --body <file>
specspec [--root <project>] update <id> --body <file> [--parent <id> ...]
specspec [--root <project>] retire <id>...
specspec [--root <project>] restore <id>...
specspec [--root <project>] list [--live | --retired] [--json]
specspec [--root <project>] show <id> [--ancestors] [--descendants] [--json]
specspec [--root <project>] context <id> [--max-bytes <n>] [--json]
specspec [--root <project>] impact <id> [--json]
specspec [--root <project>] export --format json|mermaid
specspec [--root <project>] diff --base <ref> [--target <ref>] [--json]
specspec [--root <project>] hook install
specspec [--root <project>] hook check [--json]
specspec [--root <project>] recover
```

Mutation commands accept `--json`, without fingerprints or `--expect`. Body input may use `-` for stdin so the extension needs no temporary node files. Parent changes are explicit full replacements, not additions inferred from text.

Version-three JSON envelopes contain `api_version: 3`, `ok`, `result`, and `diagnostics`. Diagnostics have stable codes, severity, paths, optional node IDs, and corrective messages. Exit codes: `0` success, `1` invalid specification or rejected mutation, `2` invocation/I/O failure. Keep prose and terminal decoration out of JSON stdout.

## 7. Git hook and revision diffs

### Hook validation

Validate the **index**, not the worktree. Load staged files with `git ls-files --stage -z` and `git cat-file`; reject conflicted stages, symlink modes, nested paths, bad schemas and structural failures, not manual-edit provenance. Partially staged files must be checked in precisely the form that will be committed.

Source existence checks are advisory worktree checks and should not decide index consistency. Invoke Git without a shell and parse filenames with NUL delimiters.

Install an executable pre-commit hook that invokes the configured Python environment's `specspec hook check`. Respect Git's resolved hook path, including `core.hooksPath`, and refuse to overwrite an existing hook. Document manual chaining instead of guessing how to alter arbitrary hooks. CI should also run validation; local hooks are bypassable.

The initial installer targets the selected workspace. Repositories containing multiple independent specifications need an explicit multi-workspace hook strategy rather than an implicit recursive scan.

### Semantic diff

Load each revision without checkout and detect its own manifesto version. An absent specification in the base revision is an empty baseline. Compare by ID; separate added/removed nodes, body changes, parent changes, withdrawal changes, metadata changes, and filename-only changes.

Return base and target graph records plus edge additions/removals so the extension can display removed nodes and disconnected relationships. Compute impact from the union of old and new descendant closures. Map changed linked source files to implementation records and their requirement ancestors using references from both snapshots, including untracked live source files. Invalid snapshots yield diagnostics and an explicitly incomplete impact result.

`--base HEAD` compares against the worktree; adding `--target <ref>` compares two commits. No command writes to the index, creates commits, or changes branches.

## 8. VS Code extension

Use a `WebviewPanel` with bundled local HTML/CSS/JavaScript and a strict nonce-based Content Security Policy. Render graph relationships with SVG and node cards; escape project content with DOM text APIs. No CDN, remote renderer, or executable Markdown.

The extension has commands to open the graph and compare revisions. Select an existing workspace folder, or offer a filesystem folder picker in an empty window; resolve subfolders to the nearest project without skipping invalid nearer graphs. A configurable executable plus argument prefix supports a pipx-installed command, `uvx`, or `python -m specspec`. Spawn with `shell: false`, bound output sizes, and report missing-tool/startup errors visibly and in the SpecSpec output channel.

Development launches use a dedicated workspace file and isolated profile so opening the project does not focus a normal editor window instead. Pass an explicit local Python interpreter through `SPECSPEC_PYTHON` for development/test hosts, while honoring explicit CLI settings. Register the webview listener before loading HTML and wait for both readiness and a token-matched DOM-render acknowledgement; report timeouts and client errors instead of leaving an indefinitely blank/loading view.

### Editing

Selecting a node replaces the overview with a neighborhood view: direct parents and children stay compact, and the selected node expands to host its binding text, actual parent links, source references, and withdrawal/restoration controls. There is no editing sidebar. A **Total graph** back action returns to the overview without losing a draft; selecting a different node requires confirmation before discarding unsaved work. New nodes use the same expanded-card presentation.

Explain minimum/maximum manifesto distance through the selected color legend rather than repeating hop labels on compact parents or the expanded card. Show each child’s **downstream node count**: all distinct reachable descendants at every depth, excluding the child itself. This incorporates grandchildren and every deeper generation as potential impact context, not a promise that every edit invalidates those nodes. Deduplicate IDs within each child’s subgraph; different children’s totals may overlap and are not additive. Use target metrics for surviving nodes and base metrics for removed nodes, never the potentially cyclic revision union.

Show only linked parents in the editable parent list, with explicit removal and a separate “Add parent” candidate picker; choosing a candidate alone must not change the links. The manifesto displays no parents and offers no parent-editing controls. Text and parent changes call `update`; withdrawal and restoration use their dedicated commands; there is no acceptance action. New-node creation uses `add`. Keep original node contents with drafts and ask confirmation before overwriting externally changed node contents. Unrelated graph changes do not prevent saving. Re-read and validate current files before mutations; deleted-node drafts stay copyable rather than being recreated.

Use full IDs in messages, not webview-generated filesystem paths. The host validates messages against the current graph before invoking the CLI. Disable mutation commands for historical comparison views and untrusted workspaces. Watch canonical files and refresh after changes; coalesce events, retry incomplete saves a bounded number of times, serialize reads/writes, and retain unsaved form content/caret/camera. Compare loaded records directly to skip unchanged redraws. Invalid files retain the last valid graph visibly marked out of date and disable mutations until a valid reload; never rewrite external changes. VS Code uses its filesystem watcher; Electron watches the project parent and canonical directory, reattaching on directory replacement. Optional polling uses a configurable millisecond interval defaulting to 0/off (`specspec.pollIntervalMs`, `--poll-interval-ms` / `SPECSPEC_POLL_INTERVAL_MS`). Dispose timers/watchers on closure/project switches and report watcher errors without secretly enabling polling. Explicit refresh remains; watcher-only delivery on every mounted/network filesystem and race-free writes against noncooperating editors are not guaranteed.

### Colors and arrows

Provide **Min. Distance to Manifesto** (default), **Max. Distance to Manifesto**, and existing-node-type fill modes with legends. Compute minimum via iterative BFS and maximum via topological dynamic programming over all snapshot links, with zero at the manifesto. Deduplicate repeated edges and leave unreachable/cycle-blocked maximums unknown rather than inventing a finite value. Use target metrics for surviving nodes and base metrics for removed nodes, never the overlay union or visible placement backbone. Retain the existing distance preference as minimum and persist maximum separately. Remove on-node hop labels while retaining downstream/Git/withdrawal badges. Keep Git changes distinct through labels and patterned strokes, not by overriding type/distance fills. Neither mode expresses acceptance or confidence; label withdrawal separately. The clarified manifesto-color request fixes its accent at #d3d3d3 in every mode, with matching legends, but uses the same theme text and 15% resting/24% hover tint as other cards, not a solid light-gray fill. Shared hovered card borders turn white; high-contrast resting styles stay shared too. Keep colors, counts, focus, and draft state out of canonical metadata. Collapse linked-source review information into an informational list rather than a large orange warning paragraph.

Use Dagre for a left-to-right presentation, with origin-anchored earliest ranks rather than sink-biased network-simplex ranking. For a DAG, each node's rank is one plus its maximum parent rank; short branches remain near the manifesto even when they feed a distant shared sink. Reverse the engine input and use its RL longest-path ranker to obtain those source ranks, then reverse waypoints back to visible relationship direction. Keep shortest manifesto distance separate from visual rank. Compute all-parent ranks first, then give Dagre a deterministic deepest-parent placement backbone: this preserves those ranks but avoids sink-driven vertical stretching. Draw all non-backbone relationships through the nearest clear gaps across skipped columns, with outer gutters as fallback. This forest is a layout aid, not a dependency choice or canonical tree. Rank target relationships in the overview/current focus and base relationships for a removed selected node; extra revision links remain overlays, not live-rank constraints. Feed it stable ID/edge ordering and intrinsic border-box dimensions—not viewport dimensions or zoomed screen rectangles. Keep compact widths fixed at 264 and the expanded editor at a fixed 860-world-unit width (previously 620) to fit typical 80-column text; textarea and revision display share the host editor monospace font/size. This is not a guarantee for arbitrarily large fonts or wide glyphs. Measure intrinsic height when forms resize. The current modest spacing adjustment shortens compact height from 128 to 112 world units, increases rank gap from 128 to 140 and sibling gap from 36 to 44. These are revisable implementation constants: despite larger gaps, vertical pitch falls from 164 to 156. Verify two-line headings/badges fit and curves still clear cards. Cache unchanged layouts and preserve the focused card's screen anchor when its size changes. Resizing the window must never wrap or reorganize nodes.

Connect right to left card boundaries with d3-shape Bézier curves, without circular socket decorations. Distribute attachments over intrinsic card height, including expanded forms, to avoid artificial header-band bends. Preserve Dagre's reserved lanes across the full width of skipped columns before smoothing gaps; averaging away a waypoint can cut through a card. Historical reverse relationships remain visibly directed and can loop outside columns.

Camera-compensate stroke width to a 1.6-screen-pixel floor and arrow length to a 6-pixel floor, retaining normal world sizes at higher magnification. These are current implementation constants, not user-prescribed pixel requirements. Compensate Git dash lengths too. Keep a short straight departure and a smooth horizontal settling approach long enough for the largest supported low-zoom head. Trim the stroked line at its filled head base to prevent tip protrusion. Camera changes only update edge appearance, never node layout, forms, or canonical metadata. Test painted-stroke clearance and tangent/head joins in the actual browser at minimum zoom, not only endpoint counts. Python remains the validation/mutation authority.

### Connection hover

Hovering a node emphasizes its displayed immediate incoming/outgoing curve/head pairs in both overview and focused views, including historical and draft links. Delegate hover-capable pointer transitions through the viewport so moving between controls inside one card does not flicker. Keep hovered identity/last pointer position only in transient memory; reconcile against the actual hit-tested card after redraw or camera movement and clear on exit, blur, cancellation, or touch.

Toggle the existing SVG pair's emphasis class, mix its Git-colored ink with theme foreground for contrast, and paint incident pairs last. Keep the hovered card and its direct displayed neighbors undarkened; darken every other card with a transient brightness filter and every non-incident curve/head pair by mixing its ink with black. A link between two neighbors still darkens unless incident to the hovered card. Historical/reversed/draft links count when displayed; even the gray manifesto darkens when unrelated. Reapply membership on redraw with unchanged hovered identity. Restore all paint/filters/order on exit. Do not change paths, stroke/head dimensions, dashes, world positions, camera, native form DOM, or persisted drafts/original node records. SVG remains non-interactive. Hover emits no host or mutation messages. Verify exact edge membership, unchanged geometry/DOM identity, form interactions, and actual computed paint at normal/minimum zoom.

### Spatial camera

Use d3-zoom to transform cards and SVG together inside a clipped viewport. Keep native headlines/forms and remove permanent `will-change: transform` promotion from the world, letting browser text rasterization follow the current scale instead of enlarging a cached low-scale surface. This improved the inspected same-pose 250% before/after rendering in Windows VS Code; font antialiasing remains browser/OS/device-dependent. Do not change font sizes, duplicate text overlays, or counter-scale individual nodes. Allow unconstrained panning and bounded 12–250% magnification; layout and metrics never depend on the camera. Middle-drag/background drag pans, wheel/pinch zooms at the pointer, and buttons/keyboard actions offer framing and actual-size recovery. Preserve separate overview and per-node focus cameras across back/refresh. Do not refit on window resize; explicit framing only changes the camera.

Exclude native settings/text-control gestures, preserve the same form DOM, caret and original draft node record, and honor reduced-motion preferences for animated framing/zoom controls. Use an adaptive grid and a navigation strip outside the clipping area so controls do not cover save/review actions. Bundle pinned libraries locally with generated license notices; CSP continues to prohibit remote/executable project content. [Library rationale and limits](docs/node-canvas.md) explain why this slice uses Dagre/D3 rather than a computational node engine.

Requested behavior and the separately reasoned layout/counting/routing choices are separately represented in the [UI intentions and conclusions](docs/own-spec.md#neighborhood-ui-revision) and [origin-density/connection correction](docs/own-spec.md#origin-density-and-connection-correction).

### Git integration

Subscribe to the built-in `vscode.git` extension's repository-state notifications when available, with filesystem watching as a fallback. Show a HEAD-versus-workspace overlay by default and offer a base/target revision picker. Distinguish changed nodes, added/removed edges, and filename-only changes; show both bodies for a selected changed node. Shared Git corners are 20px/800 weight, absolutely anchored with badge-row clearance, without increasing compact card dimensions.

Do not stage or commit on the user's behalf. Users review the same canonical files in VS Code's existing source-control workflow.

Current scope is a functional graph editor, graph-diff overlay, relational LR layout, and spatial camera. Drag-to-reparent, source-symbol navigation, and large-graph virtualization remain separate follow-up work.

## 9. Source references and agent context

Use canonical project-relative POSIX paths with an optional descriptive symbol. Reject absolute paths, traversal, control characters, redundant separators/dot components, and resolved symlink escapes. Warn about missing live source files, but do not make source existence a structural prerequisite. Retired nodes may refer to removed files.

Export a selected node with its ancestor closure, then clearly separated direct children and live siblings, using `sibling_ids` rather than `proposal_ids`. Deduplicate and order deterministically. Return complete node records without a snapshot fingerprint.

Never silently truncate binding text. Measure the actual serialized response, including its envelope and omission metadata, against the requested byte budget. If the selected node and required ancestors do not fit, return a budget error. Omit optional context only with an explicit omission list. Project text is data, not instructions to execute commands or override the agent's operating rules.

## 10. Build sequence and verification

1. **Python package and read/write core:** strict hash-free format, graph validation, CLI, transactional init/add/update/withdrawal operations, and recovery.
2. **Git integration:** staged validation, hook installation, revision snapshots, semantic diffs, and old/new impact analysis.
3. **VS Code slice:** graph rendering, node creation/editing, HEAD/workspace overlays, and commit-to-commit comparisons through the CLI.
4. **Dogfooding and distribution:** installable wheel, package checks, CI, editor packaging, and risk-proportionate self-specification review.

Test malformed frontmatter, duplicate IDs, cycles, multi-parent graphs, withdrawal failures, current-only schema rejection and interrupted-write recovery, valid manual changes, watcher/polling/draft conflicts, symlink/path escapes, comments/body preservation, interrupted mutations, invalid/partial external saves, partial staging, hook non-overwrite, slug renames, removed edges, and missing/unsupported revision formats. Run CLI integration tests in disposable repositories. Test Python on Windows and Linux; compile the extension and manually verify its VS Code UI before calling editor behavior production-ready.

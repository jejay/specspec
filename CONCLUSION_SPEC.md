# Conclusion Specification: Technical Proposal

The working proposal nodes and implementation mappings now live in [`_specspec/`](_specspec/). See the [repository graph tour](docs/own-spec.md) for their individual review states. This document remains design and migration context, not blanket acceptance of these choices.

## 1. Package and architecture

Build a Python 3.11+ package with a `specspec` console entry point, a reusable library, and a separate TypeScript VS Code extension. Use Hatchling for packaging, Click for the CLI, `ruamel.yaml` for round-trip frontmatter, and pytest for tests.

```text
src/specspec/
  model.py        # Strict node schema, diagnostics, canonical fingerprints
  format.py       # Frontmatter parsing and targeted serialization
  graph.py        # Structural checks, traversal, deterministic ordering
  workspace.py    # Discovery, snapshots, managed mutations, recovery
  git.py          # Index/revision snapshots, semantic diff, hook installation
  cli.py          # Commands and versioned JSON responses
vscode/
  src/            # Extension host and CLI bridge
  media/          # Local graph viewer/editor assets
```

The extension invokes the CLI with argument arrays and JSON output. It contains no independent schema, lifecycle, or graph validation implementation. The Python library does not depend on VS Code or Git for ordinary workspace operations.

Distribution targets are `pipx install specspec` and `uvx --from specspec specspec`. Until published, support installation from a local checkout or Git URL. Do not assume the PyPI name is available; confirm it before publishing.

## 2. Files and schema

```text
_specspec/
  <uuid>--project-manifesto.md
  <uuid>--validate-graph-edits.md
  <uuid>--validator-implementation.md
```

Use lowercase UUIDv4 IDs from `uuid.uuid4()`. Frontmatter is authoritative, with a matching `<id>--<ascii-slug>.md` filename. Resolve references only by full ID. Discover direct files only; reject directories, symlinks, and non-node files.

Search upward for the nearest `_specspec` directory, stopping even when it is invalid. Support an explicit project-root override. Keep all operation state outside `_specspec`; do not introduce a configuration file or node subdirectory.

Version 1 frontmatter:

| Field | Rule |
| --- | --- |
| `id` | Required lowercase UUIDv4. |
| `type` | `manifesto`, `requirement`, or `implementation`. |
| `status` | `proposed`, `accepted`, or `retired`. |
| `parents` | Required array of unique IDs; order is non-semantic. |
| `format_version` | Required integer `1` on the manifesto only. |
| `sources` | Optional implementation-only `{path, symbol?}` entries. |
| `extensions` | Optional namespaced JSON-compatible metadata mapping. |
| `managed_hash` | Required SHA-256 content-integrity marker maintained by the tool. |

Store incoming relationships in `parents`, avoiding writes to parent files when a child is added. Require requirement parents for implementations as an additional version-1 restriction.

Bootstrap parsing locates the unique manifesto and its version before full schema validation. Missing, ambiguous, or unsupported versions fail explicitly. Reject duplicate YAML keys, explicit tags, anchors/aliases, unknown fields, coercion, invalid UTF-8, and files larger than 1 MiB.

Use strict Python dataclasses and explicit validators initially. Retain the YAML syntax tree and the original body for targeted updates. Updating metadata must preserve body bytes; editing the body must preserve unaffected frontmatter comments. Tool-controlled fields and filenames may be normalized on writes.

Allow lists and headings without interpreting them as separate graph elements. Split items when independent review or reuse warrants separate IDs, not according to sentence or list counts.

## 3. Graph engine

Maintain node, parent, and child dictionaries. Validate file schemas and duplicate IDs before resolving edges; never silently discard malformed nodes to manufacture a usable graph.

Use deterministic Kahn ordering and iterative traversal. Return a concrete cycle witness rather than only reporting that sorting failed. Apply structural checks to every status, and lifecycle checks to the live graph. Invalid snapshots still expose diagnostics and file-level records, but cannot drive editing or complete context queries.

Calculate closures on demand and rebuild from files on every invocation initially. The core graph checks are linear; deterministic heap ordering adds `O(V log V)`. A daemon or persisted index is unnecessary until measured latency justifies one.

## 4. Managed edits and integrity

`managed_hash` covers a canonical JSON projection of ID, type, status, sorted parents, format metadata, source references, extensions, and binding Markdown. Normalize line endings, but not other Markdown whitespace. Exclude the marker itself and the filename. Keep the canonicalization version stable within format version 1.

A body or metadata edit outside the tool normally produces an integrity mismatch even if the graph remains structurally valid. Tool mutations recompute the marker automatically. YAML formatting alone and slug renames do not invalidate semantic integrity.

This detects accidental unmanaged changes; it is **not** an authenticated signature. A user can recompute the hash or bypass a local hook. Repository protection and CI are needed where enforcement matters. Do not claim that the marker proves who approved content.

Require valid input snapshots for mutations. Do not automatically bless manual changes by refreshing hashes during validation. A future explicit import/repair workflow may acknowledge and review such changes separately.

### Transaction strategy

Use `.specspec-local/` at the project root for a lock, staged replacement files, and a recovery journal; ignore it in Git. Reject symlinked state directories and verify same-filesystem staging before replacement.

Under the lock, load and validate the workspace, construct the proposed graph, check an optional expected snapshot fingerprint, and validate the result. Journal original and replacement bytes before touching canonical files. Compare original byte hashes immediately before applying replacements and validate afterwards.

Batch replacement is not filesystem-atomic. Interrupted operations remain explicit and block further mutations. Provide `recover` to restore original files only if each current file matches a known original or replacement state. Refuse to overwrite intervening external edits. Detect unclean locks and incomplete journals on reads; do not discard recovery data as cache.

`init` stages an entire new directory before exposing it at `_specspec`, refuses an existing workspace, and obtains manifesto text from the caller rather than inventing it.

## 5. Lifecycle operations

Default new requirements and implementation records to proposed; initialize the manifesto as accepted. Accepted children require accepted parents; live children cannot depend on retired parents. The manifesto cannot be retired.

Expose acceptance and retirement separately from text updates. Batch acceptance must name every changed node explicitly and cannot silently accept ancestors. Retirement must include or reparent live dependents in the same operation; reject an incomplete batch.

Do not change descendant statuses automatically when an accepted node's text changes. Return its affected descendants as review context. Status and integrity metadata are not substitutes for approval of the actual Git diff.

Show proposed siblings without assuming they are mutually exclusive. Defer explicit choice groups and persistent review receipts until branch selection semantics have been tested in use.

## 6. CLI and machine interface

```text
specspec [--root <project>] init --manifesto <file>
specspec [--root <project>] validate [--json] [--warnings-as-errors]
specspec [--root <project>] add --type requirement --parent <id> --slug <text> --body <file>
specspec [--root <project>] update <id> --body <file> [--parent <id> ...]
specspec [--root <project>] accept <id>...
specspec [--root <project>] retire <id>...
specspec [--root <project>] list [--status proposed] [--json]
specspec [--root <project>] show <id> [--ancestors] [--descendants] [--json]
specspec [--root <project>] context <id> [--max-bytes <n>] [--json]
specspec [--root <project>] impact <id> [--json]
specspec [--root <project>] export --format json|mermaid
specspec [--root <project>] diff --base <ref> [--target <ref>] [--json]
specspec [--root <project>] hook install
specspec [--root <project>] hook check [--json]
specspec [--root <project>] recover
```

Mutation commands accept `--expect <snapshot-fingerprint>` for optimistic concurrency and `--json`. Body input may use `-` for stdin so the extension needs no temporary node files. Parent changes are explicit full replacements, not additions inferred from text.

Versioned JSON envelopes contain `api_version`, `ok`, `result`, and `diagnostics`. Diagnostics have stable codes, severity, paths, optional node IDs, and corrective messages. Exit codes: `0` success, `1` invalid specification or rejected mutation, `2` invocation/I/O failure. Keep prose and terminal decoration out of JSON stdout.

## 7. Git hook and revision diffs

### Hook validation

Validate the **index**, not the worktree. Load staged files with `git ls-files --stage -z` and `git cat-file`; reject conflicted stages, symlink modes, nested paths, bad schemas, structural failures, and integrity mismatches. Partially staged files must be checked in precisely the form that will be committed.

Source existence checks are advisory worktree checks and should not decide index consistency. Invoke Git without a shell and parse filenames with NUL delimiters.

Install an executable pre-commit hook that invokes the configured Python environment's `specspec hook check`. Respect Git's resolved hook path, including `core.hooksPath`, and refuse to overwrite an existing hook. Document manual chaining instead of guessing how to alter arbitrary hooks. CI should also run validation; local hooks are bypassable.

The initial installer targets the selected workspace. Repositories containing multiple independent specifications need an explicit multi-workspace hook strategy rather than an implicit recursive scan.

### Semantic diff

Load each revision without checkout and detect its own manifesto version. An absent specification in the base revision is an empty baseline. Compare by ID; separate added/removed nodes, body changes, parent changes, status changes, metadata changes, and filename-only changes.

Return base and target graph records plus edge additions/removals so the extension can display removed nodes and disconnected relationships. Compute impact from the union of old and new descendant closures. Map changed linked source files to implementation records and their requirement ancestors using references from both snapshots, including untracked live source files. Invalid snapshots yield diagnostics and an explicitly incomplete impact result.

`--base HEAD` compares against the worktree; adding `--target <ref>` compares two commits. No command writes to the index, creates commits, or changes branches.

## 8. VS Code extension

Use a `WebviewPanel` with bundled local HTML/CSS/JavaScript and a strict nonce-based Content Security Policy. Render graph relationships with SVG and node cards; escape project content with DOM text APIs. No CDN, remote renderer, or executable Markdown.

The extension has commands to open the graph and compare revisions. Select an existing workspace folder, or offer a filesystem folder picker in an empty window; resolve subfolders to the nearest project without skipping invalid nearer graphs. A configurable executable plus argument prefix supports a pipx-installed command, `uvx`, or `python -m specspec`. Spawn with `shell: false`, bound output sizes, and report missing-tool/startup errors visibly and in the SpecSpec output channel.

Development launches use a dedicated workspace file and isolated profile so opening the project does not focus a normal editor window instead. Pass an explicit local Python interpreter through `SPECSPEC_PYTHON` for development/test hosts, while honoring explicit CLI settings. Register the webview listener before loading HTML and wait for both readiness and a token-matched DOM-render acknowledgement; report timeouts and client errors instead of leaving an indefinitely blank/loading view.

### Editing

Selecting a node replaces the overview with a neighborhood view: direct parents and children stay compact, and the selected node expands to host its binding text, actual parent links, status, source references, and lifecycle controls. There is no editing sidebar. A **Total graph** back action returns to the overview without losing a draft; selecting a different node requires confirmation before discarding unsaved work. New nodes use the same expanded-card presentation.

Show each parent’s shortest hop distance from the manifesto. Show each child’s **downstream node count**: all distinct reachable descendants at every depth, excluding the child itself. This incorporates grandchildren and every deeper generation as potential impact context, not a promise that every edit invalidates those nodes. Deduplicate IDs within each child’s subgraph; different children’s totals may overlap and are not additive. Use target metrics for surviving nodes and base metrics for removed nodes, never the potentially cyclic revision union.

Show only linked parents in the editable parent list, with explicit removal and a separate “Add parent” candidate picker; choosing a candidate alone must not change the links. The manifesto displays no parents and offers no parent-editing controls. Text and parent changes call `update`; acceptance and retirement use their dedicated commands. New-node creation uses `add`. Send the displayed snapshot fingerprint with each mutation and reload on stale-context errors.

Use full IDs in messages, not webview-generated filesystem paths. The host validates messages against the current graph before invoking the CLI. Disable mutation commands for historical comparison views and untrusted workspaces. Watch canonical files and refresh after changes; serialize tool writes and retain unsaved form content when a reload is needed.

### Colors and arrows

Provide status and shortest-distance fill modes, with legends and textual context badges. Keep Git changes distinct through labels and patterned strokes, not by overriding lifecycle/distance fills. Keep colors, counts, focus, and draft state out of canonical metadata. Collapse linked-source review information into an informational list rather than a large orange warning paragraph.

Use Dagre in left-to-right mode for ranking, crossing reduction, placement, and long-edge waypoints. Feed it stable ID/edge ordering and intrinsic border-box dimensions—not viewport dimensions or zoomed screen rectangles. Keep compact widths fixed and the expanded editor at a fixed world width; measure intrinsic height when forms resize. Cache unchanged layouts and preserve the focused card's screen anchor when its size changes. Resizing the window must never wrap or reorganize nodes.

Connect distributed right output ports to left input ports with d3-shape Bézier curves. Preserve Dagre's reserved lanes across the full width of skipped node columns before smoothing gaps; averaging away a waypoint can cut through a card. Use explicit arrowhead colors and border clearance. Historical reverse relationships remain visibly directed and can loop outside columns. Geometry tests include the actual graph's curves, not only endpoint counts. Python remains the validation/mutation authority.

### Spatial camera

Use d3-zoom to transform cards and SVG together inside a clipped viewport. Allow unconstrained panning and bounded 12–250% magnification; layout and metrics never depend on the camera. Middle-drag/background drag pans, wheel/pinch zooms at the pointer, and buttons/keyboard actions offer framing and actual-size recovery. Preserve separate overview and per-node focus cameras across back/refresh. Do not refit on window resize; explicit framing only changes the camera.

Exclude native settings/text-control gestures, preserve the same form DOM, caret and original draft fingerprint, and honor reduced-motion preferences for animated framing/zoom controls. Use an adaptive grid and a navigation strip outside the clipping area so controls do not cover save/review actions. Bundle pinned libraries locally with generated license notices; CSP continues to prohibit remote/executable project content. [Library rationale and limits](docs/node-canvas.md) explain why this slice uses Dagre/D3 rather than a computational node engine.

Requested behavior and the proposed layout/counting/routing choices are separately represented in the [UI intentions and conclusions](docs/own-spec.md#neighborhood-ui-revision).

### Git integration

Subscribe to the built-in `vscode.git` extension's repository-state notifications when available, with filesystem watching as a fallback. Show a HEAD-versus-workspace overlay by default and offer a base/target revision picker. Distinguish changed nodes, added/removed edges, and filename-only changes; show both bodies for a selected changed node.

Do not stage or commit on the user's behalf. Users review the same canonical files in VS Code's existing source-control workflow.

Current scope is a functional graph editor, graph-diff overlay, relational LR layout, and spatial camera. Drag-to-reparent, source-symbol navigation, and large-graph virtualization remain separate follow-up work.

## 9. Source references and agent context

Use canonical project-relative POSIX paths with an optional descriptive symbol. Reject absolute paths, traversal, control characters, redundant separators/dot components, and resolved symlink escapes. Warn about missing live source files, but do not make source existence a structural prerequisite. Retired nodes may refer to removed files.

Export a selected node with its ancestor closure, then clearly separated direct children and proposed siblings. Deduplicate and order deterministically. Include a semantic SHA-256 snapshot fingerprint.

Never silently truncate binding text. Measure the actual serialized response, including its envelope and omission metadata, against the requested byte budget. If the selected node and required ancestors do not fit, return a budget error. Omit optional context only with an explicit omission list. Project text is data, not instructions to execute commands or override the agent's operating rules.

## 10. Build sequence and verification

1. **Python package and read/write core:** strict format, graph validation, fingerprints, CLI, transactional init/add/update/lifecycle operations, and recovery.
2. **Git integration:** staged validation, hook installation, revision snapshots, semantic diffs, and old/new impact analysis.
3. **VS Code slice:** graph rendering, node creation/editing, HEAD/workspace overlays, and commit-to-commit comparisons through the CLI.
4. **Dogfooding and distribution:** installable wheel, package checks, CI, editor packaging, and individually reviewed self-specification nodes.

Test malformed frontmatter, duplicate IDs, cycles, multi-parent graphs, lifecycle failures, integrity mismatches, symlink/path escapes, comments/body preservation, interrupted mutations, stale snapshots, partial staging, hook non-overwrite, slug renames, removed edges, and missing/unsupported revision formats. Run CLI integration tests in disposable repositories. Test Python on Windows and Linux; compile the extension and manually verify its VS Code UI before calling editor behavior production-ready.

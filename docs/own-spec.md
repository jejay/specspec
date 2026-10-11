# SpecSpec's own specification

This checkout is a ready-to-use example. Its working graph is in [`_specspec/`](../_specspec/);
do **not** run `init` here. Canonical nodes and schema conversion are maintained
through the Python CLI in this checkout. Manual Markdown edits are permitted by
the product; there are no content markers or fingerprints in the current schema.

## Review is a spectrum, not a node workflow

The [risk-proportionate review intention](../_specspec/a3cad33b-c1f9-4903-8394-9e6cd3cc5b73--risk-proportionate-review.md)
records the user's correction: review effort and confidence are not binary stages.
Users will often spend more attention on earlier intentions near the manifesto and
less on later, readily revisable conclusions. This is an expected allocation of
attention, not a depth-based score, quota, or guarantee that a deep choice is safe.
Risky or consequential details can deserve extra scrutiny anywhere.

When the user judges an implementation attempt worth its uncertainty and token
cost, the developed graph is as reviewed as needed for that attempt. There is no
additional individual node sign-off gate. Implementation and feedback can inform
the next revision; proceeding does not make a conclusion permanent or correct.

The graph keeps intentions and conclusions separately addressable through their
relationships, explanations, and provenance. [`INTENTION_SPEC.md`](../INTENTION_SPEC.md)
is the original, unchanged source. [`CONCLUSION_SPEC.md`](../CONCLUSION_SPEC.md)
records technical reasoning, not an approval queue. Git shows newness and changes
relative to the selected base; linked-source impact is informational review context.

## Manual Markdown and watcher synchronization correction

The user's [manual-edit intention](../_specspec/5c2b23ba-7bbc-4458-b63e-808e58cd7059--editable-markdown-and-live-sync.md)
explicitly removes fingerprints and `managed_hash`: the CLI/UI remain recommended,
but consenting adults may edit Markdown directly. Actual schema/DAG checks remain.
The separate [hash-free/watcher conclusion](../_specspec/93224022-0c11-4260-b09e-2925b7aacf0f--hash-free-schema-and-watcher-reconciliation.md)
chooses format/API 3 and direct record/byte comparisons, not replacement hashes.
The old content-integrity conclusion is withdrawn after reconnecting live dependents.
The [current implementation/evidence record](../_specspec/7408785c-616b-4729-89c6-0c9987c96d16--hash-free-markdown-sync-implementation.md)
links the backend, shared session, both watcher adapters, polling configuration and tests.

Both working graphs were converted through `migrate`. Old v1/v2 Git revisions
remain readable with obsolete hashes ignored; history/receipts are not rewritten.
Migration preserves IDs, body bytes, links, sources, extensions and comments while
removing hash/approval metadata. The CLI has no `--expect` or fingerprint output.
Tool locks, original-byte replacement checks, journal/recovery, read-only history
and workspace authorization remain transaction/consistency protections.

Both hosts synchronize through coalesced filesystem events and bounded read retries.
Electron watches the parent too, reattaching after canonical-directory replacement.
Optional polling defaults to **0/off**: VS Code `specspec.pollIntervalMs`, Electron
`--poll-interval-ms` or `SPECSPEC_POLL_INTERVAL_MS`. No implicit polling fallback is
installed. Unchanged records don't redraw; explicit Refresh remains available.
Watcher-only delivery is not guaranteed for every mounted/network filesystem.

Clean forms refresh. Dirty forms/caret/cameras and original node records survive;
unrelated changes don't block saving. Same-node overwrites ask confirmation. Deleted
node drafts remain visible/copyable. Invalid files keep the last valid graph marked
out of date and disable mutations until valid, without rewriting external files.
Arbitrary editors need not honor locks; universal race-free writes are not claimed.

## Approval-free schema revision (preceding design)

The separate [Git-newness and withdrawal conclusion](../_specspec/ca580dc7-c7fa-48bc-91b1-59243144a0bf--git-newness-and-withdrawal-schema.md)
chooses format/API version 2, an explicit managed migration, and a withdrawal flag:

- No `status: proposed` / `status: accepted`, accept command, approval filter,
  parent-approval dependency, or confidence slider.
- Ordinary nodes have no stored review stage. Optional `retired: true` means
  withdrawn, retained as design history. Restoration does not claim approval.
- A live node cannot depend on a retired parent; the manifesto cannot be retired.
  These are withdrawal/structure rules, not review obligations.
- Git added/changed/removed/renamed labels and source-impact hints stay derived.
- Old version-one Git revisions remain readable. Approval fields are normalized
  away without changing historical bytes. The later v3 reader ignores old hashes.
- `migrate` now converts a valid v1/v2 workspace to v3 in one journaled transaction,
  preserving IDs, paths, body bytes, links, sources, extensions, and unaffected
  comments. Ordinary tool writes require explicit conversion first.

The repository's current graph was converted through that command. It retains
withdrawn explanations of the old [approval lifecycle](../_specspec/ff0c8e51-7aaa-4b13-97db-9623dc70d87c--proposal-lifecycle.md),
[version-one schema](../_specspec/d51d6da3-4142-4fc7-b593-d935ee5fdf6f--version-one-node-schema.md),
[review receipts](../_specspec/4607b83d-48dc-4452-a65f-bbd97209e46c--review-context-receipts.md),
and [TypeScript CLI candidate](../_specspec/d570abae-219c-4f3b-a5e4-3a4144fdfcee--typescript-cli-candidate.md).
Live dependents were explicitly reconnected before retiring superseded choices.
This is actual design history, not dummy display data or a new approval taxonomy.

## Neighborhood UI revision

The user-requested intentions remain separate from the implementation conclusions:

- [Focused editing without a sidebar](../_specspec/ee57a451-059d-426b-868e-e898c2503082--focused-node-editing.md).
- [Relationship context and all-depth downstream impact](../_specspec/2f6ee5bd-9014-4a0c-8677-53ecbab93f92--visible-relationship-context.md).
- [Selectable, non-approval graph colors](../_specspec/fc78af57-8c98-4dc5-9cc4-e590d4594cf2--selectable-graph-colors.md).
- [Readable arrows](../_specspec/e3494686-5da4-40f5-a622-f823c2e0c9b2--readable-relationship-arrows.md).
- Conclusions: [local focus/derived context](../_specspec/2b6a0e4e-f07f-4932-b58b-40348d4c3ac1--local-focus-and-derived-context.md)
  and [semantic fills/boundary routing](../_specspec/1f2e42c3-331f-4c1c-adc7-897f9bf2e004--semantic-colors-and-boundary-routing.md).

Downstream counts include every deeper descendant, not just the next generation.
Count unique IDs per child, excluding that child; overlapping child totals are not
additive. Metrics are potential impact, not a declaration of invalidation or review.
Minimum-distance-first fills, maximum distance, and existing node types replace
the obsolete status mode. The later label-removal correction is described below.

## Blender-style canvas revision

Three user intentions describe the outcome without prescribing a library:

- [Left-to-right development](../_specspec/c93ab412-77b7-4849-a556-d8e3994b825b--left-to-right-graph-flow.md).
- [Viewport-independent arrangement](../_specspec/18d1da0d-8bc3-4d58-8720-8ce194a74d1b--viewport-independent-relational-layout.md).
- [Smooth navigation](../_specspec/a723adc8-d69d-4e60-8b4f-0997ab8f4d1d--smooth-node-canvas-navigation.md).

Separate conclusions choose [Dagre/D3 layered routing](../_specspec/fbaee7c1-4c20-47ab-afd2-ae0503d428b5--dagre-layered-world-and-curved-links.md)
and [an edit-safe camera](../_specspec/d70cdad5-5e03-4200-ac75-74cf6514e56c--d3-camera-and-edit-safe-gestures.md).
The [library rationale](node-canvas.md) documents alternatives and limitations.
A library choice remains revisable without rewriting the user intention.

## Origin density and connection correction

The follow-up intention asks for [dense development near the manifesto](../_specspec/cbcde9ec-5c0b-480e-9401-cf50a4bfeb96--manifesto-centered-graph-density.md).
The [arrow intention](../_specspec/e3494686-5da4-40f5-a622-f823c2e0c9b2--readable-relationship-arrows.md)
asks for minimum visible strength at low zoom, no round connectors, and natural
curved-to-arrow transitions. Separate conclusions choose:

- [Earliest source ranks](../_specspec/4254f33d-ce29-4e33-830e-28a8edd2a51c--root-anchored-earliest-ranks.md).
- [Compact rank-preserving placement](../_specspec/c2ed5444-b7b2-4c2a-901c-ab1ba64e5e54--compact-rank-backbone-placement.md).
- [Scale-stable tangent arrows](../_specspec/10ef1cdc-62a6-4212-8387-704d3cbbeeb4--scale-stable-tangent-arrow-connections.md).

The earlier 42-node snapshot's six immediate root children occupy rank one rather
than ranks 1–5 under the preceding heuristic. This is observed improvement, not a
universal density guarantee or a review score. Ranking respects every parent and
remains distinct from shortest-hop context. All relationships remain rendered.

## Node-hover connection emphasis

The [readable-arrow intention](../_specspec/e3494686-5da4-40f5-a622-f823c2e0c9b2--readable-relationship-arrows.md)
now asks that hovering a node also highlights its immediate incoming and outgoing
curves and arrowheads, without requiring selection. A separate [transient incident-emphasis conclusion](../_specspec/1ba7e336-cdc2-46a9-8118-4b8f9e92057b--transient-incident-connection-emphasis.md)
chooses delegated pointer events, theme-aware contrast, and SVG pair ordering.

This applies to compact and expanded cards, including form controls, historical
relationships, and unsaved draft links. Highlighting keeps Git hues/dashes and
existing geometry; leaving restores normal paint. Hover is not saved in metadata,
drafts, or camera preferences, and sends no host/CLI messages. Redraw and camera
changes reconcile the actual card under the last pointer rather than keeping a
stale highlight. Tests cover direct membership, paired heads, native drafts/caret,
leave/blur/touch, revision/draft views, and computed browser paint at minimum zoom.

## Minimum/maximum distance, spacing, and headline correction

The updated [color intention](../_specspec/fc78af57-8c98-4dc5-9cc4-e590d4594cf2--selectable-graph-colors.md)
asks for **Min. Distance to Manifesto** and **Max. Distance to Manifesto**.
The [relationship-context intention](../_specspec/2f6ee5bd-9014-4a0c-8677-53ecbab93f92--visible-relationship-context.md)
now removes repetitive on-node hop labels while retaining child downstream counts.
[Origin density](../_specspec/cbcde9ec-5c0b-480e-9401-cf50a4bfeb96--manifesto-centered-graph-density.md)
asks for only slightly larger gaps; [navigation](../_specspec/a723adc8-d69d-4e60-8b4f-0997ab8f4d1d--smooth-node-canvas-navigation.md)
asks for crisp headlines at high zoom.

Separate conclusions choose [revision-local path bounds](../_specspec/f65750b7-0e8c-4014-b209-e2b480ab26d2--revision-local-distance-bounds.md)
and [unhinted native text](../_specspec/02a4e457-d709-40af-979c-1216064b1f82--unhinted-high-zoom-dom-text.md).
Minimum/maximum count shortest/longest directed paths from the manifesto in each
full snapshot, never the focused subset, placement backbone, or revision union.
The old distance preference remains minimum; maximum and type are alternatives.
The expanded card also loses distance text. Git/withdrawal/downstream cues remain.

Compact height falls 128 → 112 world units while rank/sibling gaps grow modestly
128 → 140 / 36 → 44; net vertical pitch is smaller. The permanent compositor hint
is removed without changing fonts, camera, native forms, or intrinsic dimensions.
Installed VS Code checks passed with 51 nodes and inspected same-pose 250% text
screenshots show clearly sharper rendering. Tests check bounds, deep/defensive
traversal, revision isolation, labels/legends/preferences, native drafts/caret,
card fit, unchanged geometry, and existing hover/arrow/navigation protections.
These rendering/spacing choices remain revisable, not canonical scores or universal
font-quality/performance guarantees.

## Shared hosts, branding and the preceding Activity Bar slice

The user's new [portable experience](../_specspec/5563649e-f76e-4c59-8e1d-52f60be938ee--host-independent-graph-experience.md),
[main-editor access](../_specspec/6f69c873-0ab4-450b-b306-791102affe95--activity-bar-graph-entry.md),
[brand](../_specspec/c1d04e2d-2e56-4096-9549-b66141b46ebd--dachshund-brand.md) and
[Git comparison](../_specspec/51c3e963-674e-4d5d-bd7a-b8d63649e1c8--git-graph-comparisons.md)
outcomes remain separate from the [shared renderer/session](../_specspec/65f28474-18be-46f8-89f6-b9ce30a0ec96--shared-ui-and-host-session.md),
[isolated Electron](../_specspec/449d5e44-2d5f-4c30-b4f3-9207b21b6286--isolated-electron-cli-shell.md),
[withdrawn WebviewView](../_specspec/e5c7bf6a-99d2-4173-94d4-a73cb796f470--activity-bar-webview-view.md),
[minimal icon](../_specspec/a1595f98-cae9-4593-aae9-baff7789b435--minimal-themed-dachshund-icon.md) and
[themed title/corner](../_specspec/037c4383-1934-4181-96e5-9fc3b2958e2f--theme-git-headlines-and-corner-letters.md) choices.
See [the plan/verification boundary](platforms.md) and [desktop run guide](../electron/README.md).

`graph-ui-common` owns the native canvas and guarded Python-backed operations. VS Code
hosts it in native node-file custom editors and independent main-editor panels;
Electron supplies a restricted preload/main adapter. Both use the same code, not hand-maintained copies. Project-scoped persistence,
inline forms, stale drafts, read-only history, backend integrity and native gestures stay
intact. Later [Claude Code/Codex integration](../_specspec/cbd93667-ac3b-4461-9e9d-d9ed3da6d373--later-agent-host-integration.md)
is still an intention, not an implemented connector.

The preceding sidebar-host choice is now withdrawn; the native-editor correction
below removes the container. Its original placement evidence remains history.
The proposed container `order: 4` was corrected after source/real-host inspection:
VS Code's supported contribution API assigns extension containers after built-ins.
Drag the dog below Run/Debug if desired; we don't override user layout or use private APIs.
A/M/D titles/corners read current theme tokens (M uses modified-gutter blue); pure rename
keeps R, and source-only/withdrawal cues do not masquerade as M/D. Electron supplies
VS Code dark defaults. Miniature resvg and real Windows host screenshots were inspected.
Linux is a target with a configured CI/Xvfb job, not locally executed evidence.

## Native node-file editors and independent graph tabs

The user's clarification corrects [main-editor access](../_specspec/6f69c873-0ab4-450b-b306-791102affe95--activity-bar-graph-entry.md):
Activity Bar entries select sidebar containers, not large editor workspaces. The old
WebviewView conclusion is withdrawn with its live implementation reconnected. A
separate [native-document/view conclusion](../_specspec/af518184-9eb4-4612-bfda-2876b4dbeb6a--native-node-documents-and-independent-graph-views.md)
chooses file associations, `CustomTextEditorProvider`, unsaved text overlays and
per-view cameras/commit comparisons. The [implementation/evidence record](../_specspec/54ed1528-668d-4278-937b-199ed9e0f9e0--native-node-editor-implementation.md)
links the planner, ports, adapters and actual checks. See [the architecture and trade-offs](native-editors.md).

Python plans edits without writing files. VS Code applies them to native documents;
its Save/autosave/undo/recovery own ordinary file persistence, deliberately not the
Python journal. Electron retains its managed-save adapter and the same renderer.
Invalid native buffers remain repairable, raw Markdown is accessible, and CLI project
mutations refuse dirty documents. The non-writing planner never recreates deleted
files or hides runtime locks/recovery. Native form input not yet applied to a document
has a separate recoverable backup. This is not a save veto, arbitrary-panel restart
restoration, or a large-graph typing-performance guarantee.

## An independent worked planning example

The [worked-example intention](../_specspec/5e6030af-efb6-4123-a354-1afd099c5fce--worked-planning-example.md)
records the project owner's request for a Gantt/planning app that uses SpecSpec from
the start, with at least two substantial user redirects and proper Git history.
A separate [nested-graph/real-commit conclusion](../_specspec/afe92d9e-343f-4d90-8405-81eeaf4cfbeb--independent-versioned-example.md)
chooses an independent `example/gantt/_specspec/` in the existing repository.

The [example](../example/gantt/README.md) has a clearly fictional dialogue and real
spec-before-code commits. Business-portfolio → personal manual-date → workshop
forecast redirects withdraw 13/17 and 9/16 live nodes, retaining old reasoning and
runnable code in Git. The final app has a 44-node graph (22 live, 22 withdrawn),
weekday prerequisite forecasting, explicit baseline comparison, protected local
storage, and previewed JSON conversion. Narrative stages are not node approval stages.

Actual CLI receipts and a full-history verifier check original bodies/parents/sources,
original receipt relationships/content, ancestor ordering, large withdrawal sets, no code in the first spec
commit, and runnable files in every implementation commit. Both nested and parent
index snapshots are validated before each authorized commit. CI now checks both
working graphs, the original stage history, model tests, and an isolated installed-
Chromium app smoke test; remote execution is not claimed. The real local browser
passed and desktop/narrow screenshots were inspected. The example remains a bounded
educational prototype, not a production scheduler, backup, or authentication service.

## Entry points

| What to inspect | Node |
| --- | --- |
| Project purpose | [Manifesto](../_specspec/b8983d8c-3dc0-4588-b74f-17721bfc4f5c--specspec-manifesto.md) |
| Review budget and implementation risk | [Risk-proportionate review](../_specspec/a3cad33b-c1f9-4903-8394-9e6cd3cc5b73--risk-proportionate-review.md) |
| User-controlled exploration | [Revisable conclusions](../_specspec/c0943883-e3cb-4de9-8c5e-6aeb4a37dd06--revisable-conclusions.md) |
| Current hash-free file/API/sync choice | [Hash-free/watcher conclusion](../_specspec/93224022-0c11-4260-b09e-2925b7aacf0f--hash-free-schema-and-watcher-reconciliation.md) |
| Preceding approval-free choice | [Approval-free schema](../_specspec/ca580dc7-c7fa-48bc-91b1-59243144a0bf--git-newness-and-withdrawal-schema.md) |
| Managed writes | [Recoverable mutations](../_specspec/624d0f3c-391d-4575-be87-3001f16052f6--recoverable-workspace-mutations.md) |
| Shared backend | [Python JSON backend](../_specspec/6c457b0a-654e-4545-a4b4-667f467be4f3--shared-python-json-backend.md) |
| Git code and tests | [Git adapter](../_specspec/cc058342-0f01-4dc1-99bc-439b445c5a04--git-adapter-implementation.md) |
| Editor code and tests | [VS Code implementation](../_specspec/bf8d3c4f-8d01-4e66-9ff4-9413deffef78--vscode-editor-implementation.md) |
| Self-validation and documentation | [Repository dogfooding](../_specspec/36c1ce4f-e242-494c-9566-e462b51a053e--repository-dogfooding-implementation.md) |

## Explore and edit

Install the development environment as described in the [README](../README.md):

```sh
python -m specspec validate --warnings-as-errors
python -m specspec list --live --json
python -m specspec list --retired --json
python -m specspec context cc058342-0f01-4dc1-99bc-439b445c5a04 --json
python -m specspec impact 003d697b-4104-4fdf-8e05-0db572c436d0 --json
python -m specspec export --format mermaid
python -m specspec diff --base HEAD --json
```

Prepare replacement body text outside `_specspec`, then apply it through the CLI:

```sh
python -m specspec update <node-id> --body <body-file>
python -m specspec validate --warnings-as-errors
python -m specspec diff --base HEAD --json
```

Use `add --parent <id> ...` for a separate conclusion rather than rewriting an
intention to make one solution inevitable. `update --parent` replaces the complete
parent list. Keep implementation `--sources` current when code/tests move.

Review the graph/code diff to the level warranted by uncertainty and impact. There
is no accept step. Use `retire <id>...` for withdrawn explanations and `restore`
when reconsidering them; batches must leave live dependencies valid. Withdrawal
is not a statement that the node did not receive enough review.

Use `context --include-retired` to inspect a withdrawn node's full ancestry.
Commit-to-commit comparisons use `diff --base <ref> --target <ref> --json` without
checkout. Legacy revisions render through the normalized model, read-only.

## Git, checks, and recovery

CI validates this repository graph with warnings as errors. Repository tests
exercise the real graph without freezing its UUIDs, counts, or design choices.
Migration tests use original v1 fixture blobs and v2 inputs, ignore obsolete hashes,
exercise interrupted conversion/recovery, and compare staged/historical v1 and v2
snapshots in disposable repositories. No test installs hooks in this checkout.

Local hooks remain opt-in:

```sh
python -m specspec hook install
# Stage the complete intended graph and linked implementation change normally.
python -m specspec hook check
```

The checker validates the exact index, not unstaged working files. Stage all
interdependent schema changes together. Installation preserves existing hooks and
respects `core.hooksPath`; chain the check manually when another hook exists.
Neither the CLI nor editor automatically stages, commits, or changes branches.

If interrupted, retain `.specspec-local/` and run `recover`. Confirm no writer is
running before `recover --force-lock`. A migration journal restores the original
whole schema; mixed partially converted files are never blessed by a read.

## Open the graph in VS Code

Open a canonical `_specspec/<uuid>--summary.md` file: the graph opens in the main
editor, focused on that node. **Reopen Editor With → Text Editor** keeps Markdown
accessible. Split editors share node contents, with independent cameras. **Open project** /
**SpecSpec: Select Project** and Explorer folder → **SpecSpec: Open Graph** open
independent project panels and can choose `example/gantt` without another workspace.
The Activity Bar entry is removed. Resizing clips the same world rather than reflowing cards.

After installing `.[dev]` into `.venv`, run `npm --prefix graph-ui-common ci` and `npm --prefix vscode ci`, open the
repository root, and launch **Run SpecSpec on this repository** (F5). Alternatively
launch **Run SpecSpec Extension** from `vscode/`. Both use a dedicated development
workspace/profile and explicitly select the local Python interpreter. Normal
launches retain workspace trust; trust this repository when prompted.

Stop old sessions before relaunching changed code. Empty windows offer a folder
picker, subfolders resolve the nearest project, and startup errors appear in
notifications and **View → Output → SpecSpec**. CLI and extension must both use
JSON API 3. Legacy workspaces offer a confirmed **Migrate specification** action,
but history is never migrated and dirty drafts retain their original node records.

Node-file tabs edit their bound node inside its expanded neighborhood card;
selecting neighbors opens their file editors. **Save file** uses native VS Code
persistence without approval metadata. Project panels retain **Save node** through
the managed CLI, and comparisons open independent panels. **Retire**/**Restore** change withdrawal only. Distance is explained by color/legend, without on-node hop labels; child cards
show all-depth downstream impact.
**Total graph**/**Resume draft** preserve the same form, caret, and original
node contents. **Color by** selects minimum distance, maximum distance, or existing node type. Git badges and
withdrawn labels are separate; green arrows mean added relationships, not approval.

Arrangement remains relation-derived and viewport-independent. Middle/background
drag pans, wheel/pinch zooms, and buttons/keyboard actions frame the view. Cameras,
colors, ranks, and counts remain presentation state, not canonical metadata.

`npm --prefix graph-ui-common test` covers shared session/DOM/model regressions; `npm --prefix vscode test` covers the editor adapter. `npm --prefix vscode
run test:host` drives installed VS Code through a loopback Chromium debugger with
a disposable profile, requiring Node 22+. It checks approval-free controls,
withdrawn labels, three fill modes/path bounds, label-free card fit, high-zoom native
headlines, connection-hover paint, canvas geometry, pan/zoom, drafts, native gestures,
and resized curve clearance. It also checks default node-file associations and native dirty/save/undo/redo,
raw edits, split synchronization, independent cameras and invalid-buffer repair
on a compact nested graph, separately from the repository-sized canvas tests.
Only this isolated automated host disables trust.
Screenshots can be saved with `SPECSPEC_SCREENSHOT_DIR`. Full manual mutation and
revision-picker workflows and remote CI remain separate verification boundaries.

# SpecSpec's own specification

This checkout maintains its working design in [`_specspec/`](../_specspec/). Do not
run `init` here. Use the installed Python CLI to explore and edit it; direct
Markdown edits are permitted and validated on actual schema/graph consistency.
[`INTENTION_SPEC.md`](../INTENTION_SPEC.md) is the unchanged original source;
[`CONCLUSION_SPEC.md`](../CONCLUSION_SPEC.md) summarizes current technical choices.

## Current identifiers and compatibility scope

The [compact-ID intention](../_specspec/F5JaC_4=compact-random-node-identifiers.md)
and [user's follow-up](../_specspec/Oou-SvU=current-scheme-only-and-gantt-git-regressions.md)
select canonical padded RFC 4648 Base64url over **five random bytes: 40 bits**.
The full ID has seven payload symbols and one `=`, for eight characters. Keep
that equals sign in frontmatter, parent references, commands, messages and UI.
It also separates the ID from the filename summary: `XV5_rPQ=specspec-manifesto.md`.
Standard Base64's slash is unsuitable for flat filenames. Zero pad bits mean this
shape cannot have 42 independent random bits while remaining canonical Base64url.

The separate [backend conclusion](../_specspec/qowy5AI=canonical-base64url-and-current-only-backend.md)
chooses cryptographic random bytes and collision checking under the managed writer
lock against all current nodes, including withdrawn ones. Retry exact and case-only
aliases regardless of summary; validation rejects those aliases too. References
remain case-sensitive. This protects portable filenames, not global branch-merge
uniqueness or secret/authentication tokens. Mermaid uses injective ASCII-safe IDs.

Both working graphs were converted with saved old/new mappings and original bytes
through a temporary tool-managed migration. Current code retains **only the current
format/API 3 schema**: no UUID reader, old hash/approval normalization or permanent
migration command/controls. Old node files fail validation; they are not silently
converted, accepted as a usable baseline or repaired. Rekeyed persisted host
cameras/drafts are not claimed compatible; old drafts should be copied explicitly.

### Self-reference is not a historical compatibility requirement

This graph is self-referencing evolving design documentation. Validate its working
schema, context and live source references, but **Git tooling need not work or be
tested against its obsolete revisions**. An old root comparison may report an
invalid baseline or leave the current graph visible with a diff-unavailable note.
That is expected, not grounds to resurrect superseded schemes in production code.
Prior explanations and run counts remain design/evidence history, not current
compatibility contracts or proof of correctness.

The [independent Gantt history conclusion](../_specspec/YaXJpGE=independent-current-schema-gantt-history.md)
uses the Gantt project as the rigorous versioning regression corpus. Its complete
rewritten standalone history is [`gantt.bundle`](../example/gantt/history/gantt.bundle):
eight commits, three spec/code pairs, two substantial redirects and a final audit.
All tested revisions use today's node encoding/settings/tooling. The [implementation
record](../_specspec/EpO6sR4=compliant-gantt-history-and-git-verification.md) links
the actual fixture and verification. Its 123 CLI
receipts are **new actual executions**, not edited original API-2 receipts or a
claim that older commits used today's scheme. Tests clone the bundle temporarily;
no nested `.git` is installed and unrelated SpecSpec development commits are untouched.
See [the history walkthrough](../example/gantt/history/WALKTHROUGH.md).

## Review is a spectrum, not a node workflow

The [review intention](../_specspec/3wsnEjk=risk-proportionate-review.md) allocates
attention according to uncertainty, impact and the user's budget. Earlier intentions
often receive more scrutiny; depth is not a confidence score, quota or safety claim.
Once an implementation attempt is worth its risk/token cost, no individual approval
ceremony is required. Passing tests and commits are evidence, not proof or acceptance.
[Separate conclusions](../_specspec/VZvwDBY=revisable-conclusions.md) remain revisable.

No status/proposed/accepted fields, accept command, review receipt gate or score.
Optional `retired: true` means withdrawal with retained explanation, not insufficient
review. The manifesto cannot be retired; live nodes cannot depend on retired parents.
Restore changes withdrawal, never approval. Git additions/changes/removals/renames
and linked-source impact are derived relative to the selected current-schema base.

## Manual Markdown and watcher synchronization correction

The [manual-edit intention](../_specspec/Bnr6yZY=editable-markdown-and-live-sync.md)
removes managed hashes/fingerprints and provenance gates. The [hash-free/watcher
choice](../_specspec/tvic3PQ=hash-free-schema-and-watcher-reconciliation.md) retains
schema/DAG validation, byte comparisons, managed-writer locks/journals/recovery and
workspace authorization. Watchers coalesce notifications and retry incomplete saves;
Electron also watches the parent and reattaches after directory replacement.

Polling defaults to **0/off**: VS Code `specspec.pollIntervalMs`, Electron
`--poll-interval-ms` / `SPECSPEC_POLL_INTERVAL_MS`. Explicit Refresh remains.
Unchanged records do not redraw. Dirty text, caret, cameras and original records
survive; same-node overwrite asks confirmation and deleted drafts remain copyable.
Invalid external files retain the last valid graph marked out of date, disable
managed mutations and are never silently rewritten. Watchers do not guarantee
delivery on every filesystem, and noncooperating editors can race replacement.

## Neighborhood UI revision

[Focused editing](../_specspec/t8RQMdE=focused-node-editing.md) expands the selected
node in its neighborhood rather than using a second settings sidebar. Parents
are explicit actual links, with a separate candidate picker. Child downstream
counts include all unique deeper descendants, excluding that child; overlapping
totals are not additive or guarantees of invalidation/review.

[Colors](../_specspec/7woeTpk=selectable-graph-colors.md) select minimum distance,
maximum distance or existing node type. Path bounds use each complete revision,
not visible subsets, layout backbones or the revision union. Repeated on-node hop
labels are removed. Withdrawal/Git/source cues remain distinct from semantic fills.

## Blender-style canvas revision

[Left-to-right flow](../_specspec/6EmKDz8=left-to-right-graph-flow.md),
[viewport-independent arrangement](../_specspec/LtROyww=viewport-independent-relational-layout.md)
and [smooth navigation](../_specspec/XzlIEcQ=smooth-node-canvas-navigation.md) are
intentions, not library mandates. Separate choices use locally bundled Dagre/D3,
relation-derived world coordinates and a native DOM camera. Resizing clips rather
than reflows. Middle/background drag pans, wheel/pinch zooms around the pointer,
and framing/100% controls recover the view. Native forms/caret remain intact.
[Library rationale and limits](node-canvas.md) describe alternatives and boundaries.

## Origin density and connection correction

[Origin density](../_specspec/U7wDQk0=manifesto-centered-graph-density.md) uses earliest
all-parent ranks and a compact rank-preserving placement backbone; all actual
relationships still render. Minimum distance is not visual rank. Curved arrows
attach directly to card boundaries, without round connectors, retaining visible
strength at low zoom and tangent-aligned heads. Larger forms distribute attachments.
Camera changes do not change canonical links or world layout.

## Node-hover connection emphasis

Hovering a compact or expanded card emphasizes immediate incoming/outgoing
curve/head pairs, including history and draft links. Transient pointer state,
theme contrast and pair ordering preserve Git hues/dashes and existing geometry.
Leave/blur/touch clears emphasis; redraw/camera motion re-hit-tests the pointer.
Nothing is saved in metadata or sent as a host mutation.

## Minimum/maximum distance, spacing, and headline correction

Revision-local shortest/longest directed path bounds explain semantic fills via
legends. Compact cards have shorter heights and modestly larger gaps. Permanent
compositor promotion was removed to improve settled high-zoom native headline
sharpness, without changing fonts/camera/intrinsic geometry. Earlier Windows host
screenshots and tests are recorded in implementation nodes; they are not universal
font-quality or large-graph performance guarantees.

## Shared hosts, branding and the preceding Activity Bar slice

[`graph-ui-common`](../graph-ui-common/) owns one renderer and guarded session;
VS Code and [Electron](../electron/README.md) supply narrow host adapters. No
renderer/domain-rule fork, remote assets or executable project Markdown. Electron
is isolated/sandboxed with restricted preload/IPC and explicit project authorization.
Python/Git are external prerequisites. Brand artwork and a minimal themed icon are
separate. A/M/D/R titles/corners use theme tokens; source-only impact is not M,
and withdrawal is not deletion. Future agent connectors remain unimplemented.

The old Activity Bar sidebar conclusion is withdrawn. Its historical evidence
remains reasoning, not an active container, review workflow or private layout override.

## Native node-file editors and independent graph tabs

The [native-document conclusion](../_specspec/GQdmCrA=native-node-documents-and-independent-graph-views.md)
associates `**/_specspec/???????=*.md` with the main-editor graph custom editor.
Python validates the actual resource. **Reopen Editor With → Text Editor** exposes
Markdown. Split views share TextDocument contents, not cameras; independent
project/comparison panels retain their own focus/cameras. No Activity Bar container.

Python plans edits without writing files; VS Code applies native WorkspaceEdits
and owns Save/autosave/undo/redo/recovery. Unsaved buffers overlay disk snapshots.
Invalid buffers stay repairable; native Save may persist invalid text. Managed
project actions refuse dirty native documents. Electron/project saves retain the
journaled writer. These persistence lifecycles are deliberately different, not a
claim that native saves acquire Python locks or guarantee full-DAG consistency.
[Architecture and limits](native-editors.md) cover unapplied-form backups and conflicts.

## An independent worked planning example

The [Gantt app](../example/gantt/README.md) has fictional dialogue but real rewritten
spec-before-code fixture commits. Portfolio → personal → workshop redirects withdraw
13/17 and 9/16 live nodes, retaining prior reasoning. The final graph has 44 nodes
(22 live, 22 withdrawn); the app implements weekday forecasts, explicit baselines,
protected browser storage and previewed JSON conversion. It is not a production
scheduler, durable backup, authentication or resource-optimization service.

Its verifier checks all maintained Git commits, actual receipt/context/impact
results, stage ordering, both withdrawal sets, current schema, exact index and
semantic/edge/source diffs; each runnable stage's model tests execute in isolation.
Additional Gantt Git tests cover partial staging, repaired worktrees, full-identity
renames, removed/added parent edges and linked-source ancestry.

## Entry points

| Purpose | Node |
| --- | --- |
| Manifesto | [XV5_rPQ=](../_specspec/XV5_rPQ=specspec-manifesto.md) |
| Compact IDs and current-only backend | [qowy5AI=](../_specspec/qowy5AI=canonical-base64url-and-current-only-backend.md) |
| User's history/test scope correction | [Oou-SvU=](../_specspec/Oou-SvU=current-scheme-only-and-gantt-git-regressions.md) |
| Independent compliant Git fixture | [YaXJpGE=](../_specspec/YaXJpGE=independent-current-schema-gantt-history.md) |
| Writer/recovery | [6SyZ-BU=](../_specspec/6SyZ-BU=recoverable-workspace-mutations.md) |
| Shared backend | [LvYBN_4=](../_specspec/LvYBN_4=shared-python-json-backend.md) |
| Native documents | [GQdmCrA=](../_specspec/GQdmCrA=native-node-documents-and-independent-graph-views.md) |
| Working self-validation scope | [evfMtUM=](../_specspec/evfMtUM=continuous-self-validation.md) |
| Compact-ID implementation/evidence | [i7aT1lc=](../_specspec/i7aT1lc=compact-id-current-only-implementation.md) |
| Git/history/host evidence | [EpO6sR4=](../_specspec/EpO6sR4=compliant-gantt-history-and-git-verification.md) |
| Host fixture scope and initial observations | [3fWBW_g=](../_specspec/3fWBW_g=maintained-gantt-host-integration-fixtures.md) |

## Explore and edit

```sh
python -m specspec validate --warnings-as-errors
python -m specspec list --json
python -m specspec context qowy5AI= --json
python -m specspec impact F5JaC_4= --json
python -m specspec export --format mermaid
python -m specspec update <full-id> --body <body-file>
```

Use `add --parent <id> ...` for a separate conclusion, not a rewritten intention
that makes one solution inevitable. `update --parent` replaces the full parent
list. Keep source links current. No accept step; retire/restore explicit batches.

## Git, checks, and recovery

Read [AGENTS.md](../AGENTS.md) for all development checks. Before an authorized
commit, stage the complete intended change and validate both exact index snapshots
with `hook check`; working-tree validation is not a substitute. Hook installation
is opt-in and preserves existing hooks. Tools never automatically stage or commit.

Use `diff --base <current-scheme-ref> --json`. During schema conversion the old root
HEAD is intentionally not a valid baseline; review the ordinary Git patch instead.
Use the Gantt bundle for history regression checks. If interrupted, retain runtime
state and run `recover`; remove stale locks only after confirming no writer runs.
Recovery refuses intervening external edits. Process-interruption protection is not
a promise of full power-loss durability or adversarial filesystem safety.

## Open the graph in VS Code

Open a canonical equals-delimited node file or use **SpecSpec: Open Graph**.
Development installs use `.venv`, `npm --prefix graph-ui-common ci` and
`npm --prefix vscode ci`, then **Run SpecSpec on this repository** (F5). Stop old
sessions before relaunching changed code; trust the workspace when prompted.
Startup failures appear in notifications and **View → Output → SpecSpec**.

Shared/editor/desktop unit suites and optional installed-host checks are documented
in the README and host guides. Current local checks passed: 100 Python tests,
99 shared UI tests, 34 VS Code adapter tests, nine desktop unit tests, Ruff and
both working validators. All Gantt stages/model tests, current receipts/history
and the installed Chromium app smoke passed. Full Windows VS Code/Electron host
checks pass on maintained Gantt fixtures, including native node-file lifecycle.

The first optional rekeyed-root runs hit density/hover assertions; the [separate
fixture choice](../_specspec/3fWBW_g=maintained-gantt-host-integration-fixtures.md)
retains those observations. Moving the corpus did not weaken the assertions or
change production layout/hover behavior; this is not a universal arbitrary-graph
density/hover guarantee. Configured remote CI and non-Windows real-host runs are
not claimed. Prior run counts/host checks remain historical evidence.

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
maximum distance, existing node type or Git/Revision Status under the later rainbow
extension. Path bounds use each complete revision,
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

### Neutral manifesto and hover-darkening revision

The user requests a [light-gray manifesto](../_specspec/pWgqwcQ=light-gray-manifesto.md)
and [darkening outside hovered relationships](../_specspec/RlFT4io=darken-outside-hover-neighborhood.md).
The initial [rendering choice](../_specspec/6MUwTIw=stable-root-and-transient-hover-darkening.md)
misinterpreted gray as a solid pale root. The [user correction](../_specspec/iktVTRU=consistent-gray-cards-and-roomier-markdown.md)
and [shared-tint/readability choice](../_specspec/xCOHepQ=shared-card-tints-and-80-column-editing.md)
keep the gray accent but restore ordinary theme text and shared card tints: the
root is only modestly lighter than a dark canvas, with a white hover border.
White belongs only to the manifesto; other cards emphasize their semantic hue. Expanded Markdown/revision-text areas are 860 world units wide for
typical 80-column text; compact cards stay 264×112 with larger/heavier Git corners.
Connected nodes still mean direct displayed neighbors, matching incident highlighting.
Non-incident links darken even when both endpoints are neighbors. The root's base
hue remains gray; it too darkens when unrelated to the hover. These are transient
presentation changes, not selection, review scores, graph edits or new host forks.
The shared renderer applies darkening to existing cards/curve-head pairs and
reconciles it after refresh and camera motion. Windows VS Code and Electron
real-host suites passed on maintained Gantt fixtures, including normal/minimum-zoom
computed paint, CSS dark/light/high-contrast probes and unchanged geometry. Initial
concurrent runs timed out; isolated reruns passed without weakening assertions.
The [implementation/evidence record](../_specspec/BbLribU=neutral-manifesto-and-hover-darkening-implementation.md)
retains the earlier actual evidence with an explicit solid-root correction.
Current host checks verify the shared tinted root/white border, 80-column text at
13/14/16px fonts, enlarged Git-letter clearance and the existing routing/navigation
invariants. The first screenshot-enabled VS Code run passed the full canvas but
timed out in native-document checks; its unchanged isolated rerun passed.
The [current implementation record](../_specspec/AXhpgds=shared-gray-tints-wide-text-and-bold-git-corners.md)
links shared code, test evidence and font/platform limits.

### Color-preserving hover correction and regression trace

The [user correction](../_specspec/pqNhV6s=color-preserving-node-and-connection-hover.md)
rejects white borders on non-manifesto nodes and washed-out colored connections.
Spec commit `0d8d44b` (2026-10-11) overgeneralized the manifesto-only white-border
request into “all cards” in xCOHepQ=. Code commit `c2d8e15` then implemented that
global override and enforced it in tests. The parent intention requested white
only for the gray root; shared tint behavior did not authorize whitening other
semantic borders. Those conclusions are corrected explicitly, not treated as
user requests or validated by their passing tests.

The [replacement choice](../_specspec/bLBNk80=hue-preserving-hover-lightness-and-chroma.md)
keeps white only on the manifesto and raises non-root border lightness/chroma
in its own semantic hue (yellow stays strong yellow). Added/removed/draft incident
curves and heads likewise become brighter and more saturated without foreground
mixing. The washed-out mix originated in `34e72bb` (2026-10-06): 50% ink and 50%
theme foreground. Neutral normal links keep theme contrast emphasis; modified
nodes do not imply a new modified-link kind. Geometry, dashes, paired ordering,
one-hop darkening, native forms and exit restoration remain unchanged. Relative
OKLCH constants and gamut/platform limits are separate revisable choices.
The [implementation/evidence record](../_specspec/T5K4JZI=color-preserving-hover-implementation.md)
links the shared CSS and regressions. Windows VS Code and Electron host suites
passed on independent maintained-history clones, verifying computed brighter/
higher-chroma same-hue ink, root-only white borders, yellow/type/distance borders,
all node Git states and expanded cards, dark/light/contrast probes and restoration.
Captured VS Code hover screenshots were inspected. Current local checks passed:
108 shared UI, 34 VS Code, nine Electron and 111 Python tests, Ruff lint/format and
working-graph validation. This is bounded browser/platform evidence, not a claim
about every theme/custom palette, display gamut or platform.

## Shared rainbow table and Git/Revision Status

The [user request](../_specspec/Rg30CXs=rainbow-node-palette-and-revision-color-mode.md)
orders spectrum colors from violet through blue/cyan/green/yellow/orange to red,
with more intermediate colors and a similar gentle feel. The [separate choice](../_specspec/6QB9hRY=shared-rainbow-table-and-derived-revision-fills.md)
now uses nine in-gamut sRGB swatches sampled at OKLCH lightness .73/chroma .12,
hue 300 through 30 in 33.75-degree steps. The [user's follow-up](../_specspec/l3vgxN4=nine-more-distinct-rainbow-colors.md)
finds thirteen colors too close and requests nine with slightly stronger saturation.
Lightness stays unchanged; chroma increases about 9%. One hop starts violet;
nine reaches red; ten restarts violet. Node types reuse teal/violet entries. Unknown paths are
neutral, and distance/type manifesto accents remain light gray outside the cycle.

**Git/Revision Status** uses the selected comparison: A green, M/R blue, D red,
source-only affected amber, unchanged neutral gray. Rename/source labels remain
distinct; withdrawal is not deletion and direct node changes take precedence over
source impact. No comparison is explicitly labeled and neutral; unsaved new or
orphaned drafts do not invent Git changes. Existing themed titles/corners and edge
colors/dashes are independent. The new mode colors the manifesto by its comparison
kind too, in compact and expanded views, with stronger same-hue hover instead of
the neutral-root white override. Earlier all-mode gray-root descriptions are
superseded only for this new mode; no approval status or schema fields return.

The mode persists in host state without changing metrics, geometry, camera, native
form DOM/caret/drafts or original contents. Tests check independently converted
palette lightness/chroma/hue, cyclic indexing, shared-table mappings, root status
changes and mode switches, historical/removed/source-only/withdrawal distinctions,
no comparison and drafts. Real Windows host paint checks include a CLI-modified
root in an independent disposable Gantt clone and all dark/light/contrast probes.
The [initial implementation/evidence record](../_specspec/Flf59Uc=rainbow-and-revision-colors-implementation.md)
links the shared model/renderer/template/CSS and earlier thirteen-color regressions.
The [nine-color tuning record](../_specspec/ezKCR3w=nine-color-rainbow-tuning-implementation.md)
links the revised palette/mappings and current checks. The screenshot-enabled VS
Code attempt failed on a non-top-level CDP capture target; its unchanged full
rerun without screenshots passed. Electron passed with inspected screenshots.
All 115 common,
34 VS Code, nine Electron and 111 Python tests passed, as did Ruff and working
validators. Both complete Windows host suites ultimately passed sequentially;
the current tuning screenshots are from Electron. Constants and bounded host evidence remain revisable, not
accessibility/display or every-platform certification.

## Separate palette playground

The [user request](../_specspec/XLyy460=standalone-rainbow-parameter-playground.md)
and [offline/export choice](../_specspec/IAy2dGI=offline-oklch-playground-and-copyable-palette.md)
add [`tools/rainbow-playground/index.html`](../tools/rainbow-playground/index.html).
Open it directly in a browser; no server, network or installation is needed.
Count, lightness, chroma and hue endpoints drive an interactive dark/light preview,
with the current nine-color palette as defaults. Out-of-gamut samples explicitly
reduce chroma at fixed hue/lightness, rather than silently clipping RGB. Copy
parameters JSON (sufficient), full palette JSON or CSS variables back to the
assistant. Clipboard rejection falls back to selected text for manual copy.
There is no automatic palette import, graph mutation or filesystem/browser-storage
persistence. Suggested hue-based type/Git mappings remain suggestions.
The [implementation/evidence record](../_specspec/mtuhTCk=offline-rainbow-playground-implementation.md)
links the small tool, focused regressions and actual standalone file:// browser
verification. This is a parameter experiment, not universal display/accessibility
certification.

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
107 shared UI tests, 34 VS Code adapter tests, nine desktop unit tests, Ruff and
both working validators. All Gantt stages/model tests, current receipts/history
and the installed Chromium app smoke passed. Full Windows VS Code/Electron host
checks pass on maintained Gantt fixtures, including native node-file lifecycle.

The first optional rekeyed-root runs hit density/hover assertions; the [separate
fixture choice](../_specspec/3fWBW_g=maintained-gantt-host-integration-fixtures.md)
retains those observations. Moving the corpus did not weaken the assertions or
change production layout/hover behavior; this is not a universal arbitrary-graph
density/hover guarantee. Configured remote CI and non-Windows real-host runs are
not claimed. Prior run counts/host checks remain historical evidence.

# SpecSpec's current specification

[`_specspec/`](../_specspec/) is this repository's binding current graph. It describes
owner intentions, separately reasoned conclusions and actual implementation mappings.
Git predecessor trees and commit messages retain changed decisions and run evidence.
[`INTENTION_SPEC.md`](../INTENTION_SPEC.md) preserves the original owner input;
[`CONCLUSION_SPEC.md`](../CONCLUSION_SPEC.md) summarizes current technical choices.

## Planning process

The owner's preliminary process in [AGENTS.md](../AGENTS.md) is represented by:

| Element | Node |
| --- | --- |
| Implementation-mature spectrum planning | [r1wddEQ=](../_specspec/r1wddEQ=positive-current-specification-planning.md) |
| Positive current binding text | [LjbEgSo=](../_specspec/LjbEgSo=positive-current-binding-text.md) |
| Inspect/preserve owner changes | [MPOzb8A=](../_specspec/MPOzb8A=owner-change-inspection-and-preservation.md) |
| Tandem understanding and choice review | [93sqYPw=](../_specspec/93sqYPw=tandem-understanding-and-choice-review.md) |
| Agent planning and separate specification commits | [FU5NaYc=](../_specspec/FU5NaYc=agent-planning-and-specification-commits.md) |
| Depth-focused implementation and conflict reporting | [kvBgyYw=](../_specspec/kvBgyYw=depth-focused-implementation-and-conflict-reporting.md) |

Owner planning may supply direct edits. Tandem planning discusses intentions and
meaningful choices while leaving manipulation to requested agent planning. Agent
planning preserves owner input first, deepens/reconciles the graph through CLI
operations, checks the exact index and commits an agent changeset. Implementation
adds depth under established intentions and communicates conflicts/subset choices;
scope changes return to owner planning. These are agent working instructions, while
product CLI/UI staging and commits remain controlled by their users.

Precision aims at faithful implementation. Review and evidence still assess meaning
and uncertainty; the graph's position is a justification relationship. The
[review intention](../_specspec/3wsnEjk=risk-proportionate-review.md) follows the
owner's uncertainty/impact/token budget. [Revisable conclusions](../_specspec/VZvwDBY=revisable-conclusions.md)
keep solution choices independently addressable.

## Product grammar and canonical data

The [manifesto](../_specspec/XV5_rPQ=specspec-manifesto.md) leads a
[rooted DAG](../_specspec/DiIJxaQ=rooted-requirement-dag.md) of requirements and
terminal implementation leaves. [Spectrum position](../_specspec/W8_8BXA=relative-spectrum.md)
follows relationships. The flat `_specspec` directory contains direct node Markdown
files; frontmatter holds identity/type/parents and the body holds binding text.

[Compact identity](../_specspec/F5JaC_4=compact-random-node-identifiers.md) and the
[typed schema conclusion](../_specspec/qowy5AI=canonical-base64url-and-current-only-backend.md)
choose padded RFC 4648 Base64url over five random bytes: **40 bits**, seven payload
symbols and the full trailing `=`. Filename form: `<id><slug>.md`. Lock-scoped
creation retries exact/casefold collisions; validation checks portable aliases.
Current **node format 6** defines the sole supported node scheme; **API 6** defines the compact application protocol. Schema errors and
unsupported historical formats receive diagnostics. Source blob IDs address code
contents; transaction protection compares original bytes.

[Shortcut-free justifications](../_specspec/uAjln2M=shortcut-free-immediate-justifications.md)
require each direct parent to contribute ancestry. The
[shared validation choice](../_specspec/pA2ls_g=central-shortcut-validation-and-current-format-contract.md)
checks all candidates, native overlays, historical graphs and exact indexes under
one current contract, reporting alternative paths without repairing edges. Ancestor
bindings carry justification; implementations contribute bounded realizations.
Review ripple effects using both old and new graphs. See [graph structure](graph-structure.md).

[Managed transactions](../_specspec/6SyZ-BU=recoverable-workspace-mutations.md)
validate saved/candidate graphs and journal bytes/null deletions under a lock in
`.specspec-local`. Recovery recognizes known original/replacement/absence states
and preserves intervening external text. Retain interruption state and use
`recover`; clear stale locks only after confirming the writer absent.

## Physical cascade deletion and HEAD views

[Deletion/HEAD intention](../_specspec/xu6W0c4=withdraw-by-file-deletion-and-show-workspace-against-head.md),
[descendant intention](../_specspec/fuyy0Lk=cascade-delete-all-children-and-warn-if-uncommitted.md),
[ghost conclusion](../_specspec/5d5oDCM=physical-deletion-and-head-relative-ghost-views.md)
and [plan/warning conclusion](../_specspec/AuhoBoU=downstream-deletion-plans-and-uncommitted-warnings.md)
separate outcomes from the mechanism. Managed deletion includes every descendant,
including shared children. Outside parents survive unchanged. A preview reports
scope and all uncommitted affected files, including staged ones. Warned noninteractive
deletion requires `--yes`; hosts confirm and supply the reviewed plan for locked
rechecking. See [deletion commands and boundaries](deletion.md).

Default workspace views reread HEAD. Committed deleted nodes remain copyable,
read-only D ghosts through staging and disappear after commit. Historical comparisons
retain independent views. File/Git watchers provide bounded event hints, with explicit
Refresh/optional polling (default off). Native Delete requires clean project documents.
[Ghost implementation](../_specspec/JqNzSPg=deletion-only-head-workspace-implementation-and-evidence.md)
and [cascade implementation](../_specspec/huB7hcg=cascade-deletion-and-uncommitted-warning-implementation.md)
map the current code and regression seams.

## Source regions and Git consistency

[Source-region intention](../_specspec/v6xn2GU=precise-and-growing-git-tracked-implementation-source-regions.md),
[blob choice](../_specspec/jsIUeP0=stable-blob-anchors-with-derived-source-locations.md)
and [tracking contract](../_specspec/VnSF9BE=strict-and-expanding-source-range-resolution-contract.md)
use project-relative paths, full immutable SHA-1/SHA-256 blobs and multiple inclusive
ranges. Strict reports internal changes; expanding absorbs internal/contained changes.
Both exclude outer-boundary insertions and gaps. Ambiguity, deletion, unavailable
objects and mapping budgets remain explicit. Git trees retain anchor objects.

[Implementation](../_specspec/vQFml0Y=blob-source-regions-implementation-and-current-history-evidence.md)
links its own strict schema and expanding resolver/command anchors. Whole-file hints
remain usable. [The source guide](source-regions.md) documents inspection/capture/check/
reanchor, literal previews, retention and limits. Capture uses the existing
native or managed form's save owner. File-level source impact stays conservative.

[Exact-index and revision reasoning](../_specspec/Yfy0414=staged-validation-and-semantic-diffs.md)
checks staged blobs and compares full IDs/edges/sources without checkout.
Owner-configured hooks/CI call `check --staged`; adding `--sources` assesses staged
code mapping/retention. Hook files and Git operations remain under owner control.

## Shared host experience

[One renderer/session](../_specspec/YOPhqYc=shared-ui-and-host-session.md) and a
[Python domain library/CLI](../_specspec/LvYBN_4=shared-python-json-backend.md)
serve VS Code and Electron. [Native documents](../_specspec/GQdmCrA=native-node-documents-and-independent-graph-views.md)
open equals-delimited node files in the main editor with raw-text access, split
TextDocument synchronization and independent view cameras. Python plans; native
Save/autosave/undo/recovery persist documents. Invalid text remains repairable.
Electron/project actions use the managed writer. [Watch reconciliation](../_specspec/tvic3PQ=hash-free-schema-and-watcher-reconciliation.md)
retains drafts/caret/cameras and marked last-valid views during external changes.

[Electron isolation](../_specspec/3SfTeOo=isolated-electron-cli-shell.md)
constrains preload/IPC/assets and authorizes local projects with trusted launch
settings. Python/Git are external prerequisites. [Agent connectors](../_specspec/3FThKz4=later-agent-host-integration.md)
are separately scoped future transport/authorization work.

## Remote workspaces and prompt loading

[Remote intention](../_specspec/CmZafVM=vscode-remote-workspace-experience.md) and
[workspace-host boundaries](../_specspec/uY3KPsM=remote-workspace-host-and-execution-boundaries.md)
place the Node/Python/Git adapter beside real local or remote project files while
VS Code owns transport and client rendering. See [remote setup/qualification](remote-workspaces.md).

[Loading intention](../_specspec/tGpRMLM=prompt-valid-working-graph-loading.md) is
refined by [Git batching](../_specspec/wAp9Qz8=bounded-batched-canonical-git-object-reads.md),
[shared/bootstrap reads](../_specspec/3V6SdSA=version-checked-shared-and-bootstrap-reads.md),
[derived caches](../_specspec/L0KGXB8=bounded-derived-git-and-frontmatter-caches.md),
[working-first comparison](../_specspec/VDss3KM=working-first-loading-and-fresh-comparison-adoption.md)
and [measurement scope](../_specspec/FJj-9xY=loading-stage-and-remote-qualification-evidence.md).
[Loading diagnostics](loading.md) explain current controls and cache safeguards;
[investigations](investigations/vscode-loading.md) retain the motivating evidence.
[Backend realization](../_specspec/FhVjOvo=batched-git-and-verified-read-cache-implementation.md)
and [workspace/phased-host realization](../_specspec/N7IR7Fw=remote-and-phased-graph-loading-implementation.md)
map the code, diagnostic controls and verification seams.
[Superseded-read handling](../_specspec/KGvVHh0=retry-superseded-reads-without-diagnosing-invalid-files.md)
keeps generation/text races distinct from invalid files, coalescing bounded fresh
attempts while preserving the displayed presentation and mutation preflights.
[Project-scoped API channels](../_specspec/sxxzsrk=reuse-bounded-per-project-application-channels.md)
reuse interpreter lifetime with a separate read-only preview channel. Each request
still validates fresh files and Git state. [Interactive source reads](../_specspec/TpFMeZc=serve-interactive-source-previews-independently-of-background-reads.md)
bind to the published view and displayed commit, while [metadata events](../_specspec/0aNDHfQ=refresh-spotlight-metadata-from-its-own-events.md)
and [HEAD/ref watching](../_specspec/yEoFkOE=discover-git-watch-paths-asynchronously-and-coalesce-notifications.md)
coalesce their own work. The [implementation](../_specspec/HZHjxQ8=implement-responsive-source-and-metadata-read-scheduling.md)
links channels, scheduling and causal/installed regressions.
The [polling lifecycle verification choice](../_specspec/wkCbtnQ=verify-polling-shutdown-independently-of-watcher-completion.md)
separates periodic ticks from still-valid watcher hints and pending work.
[Its causal investigation](investigations/polling-test-race.md) reproduces the late
initial-discovery race and verifies shutdown/disposal with controlled clocks.

## Compact command and shared-read contract

[Compact command intention](../_specspec/0dvOn3A=compact-useful-command-interface.md)
leads the [everyday command vocabulary](../_specspec/7tMgRa8=eight-everyday-commands-and-focused-advanced-tools.md),
[readable defaults](../_specspec/sJ5dyh4=readable-default-results-and-complete-context.md),
[full review diffs](../_specspec/7kYVG_E=complete-node-aware-text-and-relationship-diffs.md)
and [compact API 6](../_specspec/cpFRqIM=compact-versioned-json-with-reconstructible-comparisons.md).
Canonical node format is **6**. The [shared read path](../_specspec/-UedVEw=shared-electron-and-vscode-graph-read-path.md)
serves both hosts with optional native overlays; [safeguards](../_specspec/nIj9fmE=compact-interface-preserves-deletion-and-source-guards.md)
and [coordinated examples/cutover](../_specspec/4ZvnSGw=current-cli-receipts-and-coordinated-protocol-cutover.md)
retain their domain and verification boundaries. The [command guide](cli.md) gives
current operational recipes; original owner source remains unchanged in AGENTS.md.
[CLI/review implementation](../_specspec/SF12qpA=compact-cli-and-full-review-implementation.md)
and [shared host implementation](../_specspec/GG_koyg=shared-read-coordinator-and-compact-host-adapter-implementation.md)
map the code and verification seams.

[Complete tree-shaped reads](../_specspec/kiOMI7I=read-complete-specification-graphs-in-a-token-conscious-tree-shaped-view.md)
serve human and agent readers with complete revision comparisons. The
[last-occurrence choice](../_specspec/T693TDw=place-full-records-at-the-last-occurrence-of-an-ordered-unfolded-walk.md)
orders selected-record projections through iterative reverse/forward DFS. The
[compact-header choice](../_specspec/nLqvWcM=keep-compact-query-rails-and-complete-parent-headers.md)
keeps two-column rails and every direct parent in full headers. The
[comparison choice](../_specspec/h3zqGZU=read-current-records-with-sparse-revision-hints.md)
uses spotlight-style HEAD/workspace defaults, complete current/base binding content
and sparse worded change hints. The [default one-line choice](../_specspec/AY1g-sU=read-each-query-binding-on-one-line-with-paragraph-separators.md)
joins single newlines with a space and longer runs with ` ¶ `; original bodies remain
exact in JSON/diff. The [compact/human presentation choice](../_specspec/B6y6hgo=offer-compact-and-human-query-presentations-with-comma-separated-lists.md)
groups sources into one comma-separated line by default; `--human` keeps logical
body lines and lists sources individually. Parent IDs always use comma-space
separators. Both modes retain the same facts and JSON. Lowercase type/status words
make the legend unnecessary, and root content aligns with its header. The [selected-record overlay](../_specspec/B71bAFk=keep-deleted-bindings-in-the-selected-record-comparison-graph.md)
keeps deleted records among current records, selecting former parents only for
deleted nodes. This projection is acyclic while original revision graphs remain
reconstructible. Normal records stay unmarked; exact text changes belong to `diff`.
The [source comparison choice](../_specspec/jWl96h0=compare-source-declarations-and-resolved-version-locations-independently.md)
separates reference-list changes, conservative linked-file impact, selected code
text and actual per-version locations under shared strict/expanding resolution.
The [contract-aware query choice](../_specspec/z9YKFeE=signal-query-source-changes-through-their-declared-tracking-contracts.md)
keeps changes permitted by strict/expanding/path-only references quiet, including
source-changed badges. Known contract transitions propagate through both original graphs. One-line
sources retain broken/uncertain/restored hints; JSON keeps complete raw source facts
and separate contract classifications. Shared file-impact reporting stays broader.
The [per-invocation batch choice](../_specspec/2doGbqA=batch-known-query-source-blobs-within-each-invocation.md)
loads known committed source blobs and anchors into the existing per-call cache,
while refs/workspace files remain fresh. [Profiling evidence](investigations/query-performance.md)
includes fixed-input equality, subprocess-count regressions and reproducible timings.
[Implementation](../_specspec/Kxh7M4Q=render-complete-tree-shaped-query-reads-with-iterative-last-occurrence-placement.md)
maps the renderer, source reader integration, CLI, plain-output golden cases and
independent temporal/structure checks. See [the query guide](query.md). Node format/API remain 6.

## Neighborhood UI revision

[Focused editing](../_specspec/t8RQMdE=focused-node-editing.md) expands the same native
form within compact direct parents/children. Actual links and candidate parents are
separate; child counts include unique all-depth descendants. [Path bounds](../_specspec/FHfnj08=revision-local-distance-bounds.md)
use full individual revisions, while [neighborhood context](../_specspec/V0xi_J8=local-focus-and-derived-context.md)
keeps potential impact understandable. Counts and distances are derived presentation.

[Relational world layout](../_specspec/LtROyww=viewport-independent-relational-layout.md)
uses left-to-right earliest ranks and a deterministic compact backbone while drawing
every relationship. [Dagre/D3](../_specspec/tgHQyx4=dagre-layered-world-and-curved-links.md)
are locally bundled. [Spatial navigation](../_specspec/mAZgRy8=d3-camera-and-edit-safe-gestures.md)
uses 12–250% pointer-anchored zoom and unconstrained pan with explicit frame/100%
controls. [Floating controls](../_specspec/FZO2_-Q=keep-navigation-in-a-compact-floating-canvas-control.md)
keep framing icons over the full canvas. [Rectangle framing](../_specspec/zs0OtME=frame-a-drawn-rectangle-with-a-one-shot-canvas-tool.md)
uses the [captured-pointer choice](../_specspec/zwevPEc=capture-rectangle-framing-in-viewport-pixels-and-invert-the-starting-camera.md):
Ctrl on Windows/Linux, Command on Mac, a latched drag through modifier release,
and framing on pointer release. Cancellation clears the transient tool. Native
text rasterizes at the current scale; routes retain low-zoom stroke/head strength
and tangent joins. [Canvas tutorial](node-canvas.md#canvas-controls) describes the gestures.

## Exact palette, hover and node shapes

[Seven swatches](../_specspec/gfAxHps=user-selected-seven-color-palette.md) are
`#bc82c9`, `#7e97e6`, `#1facce`, `#37b390`, `#92a64b`, `#ca8d3e`, `#dc7b7c`.
[Role intention](../_specspec/B87C_kI=added-green-first-and-leftover-requirement.md)
and [shared-table choice](../_specspec/6QB9hRY=shared-rainbow-table-and-derived-revision-fills.md)
map zero-based Requirement 4, Implementation 0, Added 3, M/R 1, D 6 and source-only 5.
One hop starts the table; distance repeats every seven. Revision mode colors the
manifesto too; distance/type keep its gray accent.

[Influence colors](../_specspec/zOX2L9c=color-absolute-and-relative-influence-continuously.md)
count self plus unique descendants at all depths, with a minimum of one. The
[normalization choice](../_specspec/JVHv1gc=normalize-revision-local-influence-on-a-continuous-warm-ramp.md)
uses `(c-1)/(M-1)` for Absolute influence, and cohort minimum to maximum for
Relative influence, grouping by **maximum** manifesto distance.
[Linear and logarithmic choices](../_specspec/HlpFtiA=keep-linear-and-logarithmic-influence-choices-together.md)
remain available together. Log Absolute Influence uses `log(c)/log(M)`;
Log Relative Influence uses `(log(c)-log(lo))/(log(hi)-log(lo))`, transforming
self-inclusive counts before subtracting the cohort minimum. Structural downstream
counts exclude self. All four modes share a continuous green `#4df884` → yellow `#e8d62c` → red `#ba2208` sRGB
ramp, separate from the seven swatches. Tied groups use green; the manifesto
stays gray. Full target/base revisions determine scales, never visible subsets.
[The influence realization](../_specspec/8Slagkc=render-continuous-absolute-and-cohort-relative-influence.md)
maps lazy metric ranges, compact/expanded paint, gradient legends and verification.

Cards use shared 15% resting/24% hover tint at actual size and ordinary theme text.
[Overview shapes](../_specspec/sV3uzvQ=read-the-zoomed-out-graph-as-solid-colored-node-shapes.md)
progressively fill to their painted borders as zoom decreases. The
[two-stage mixing choice](../_specspec/eqWEPJI=interpolate-node-fill-toward-its-painted-border-over-the-overview-range.md)
starts fill progression at 40% scale and reaches the painted border at 16%, separately
from ordinary arrows' 70%-to-16% quieting interval. Exact actual-size tints remain.
[Positive concise copy](../_specspec/iHpAyAE=use-concise-positive-present-tense-interface-copy.md)
keeps legends to actual color labels, with tutorials in documentation. Its
[realization](../_specspec/znpy2MA=present-concise-action-and-state-copy-across-visual-surfaces.md)
covers shared UI, host repair text and the palette playground.
[Hue-emphasizing hover](../_specspec/bLBNk80=hue-preserving-hover-lightness-and-chroma.md)
increases colored border/incident ink lightness and chroma. The neutral manifesto's
hover border is white. [Immediate-context darkening](../_specspec/6MUwTIw=stable-root-and-transient-hover-darkening.md)
is transient and preserves geometry/native forms. [Spotlight rings](../_specspec/E7O_6GU=view-local-label-cycle-with-inset-border.md)
paint available selected IDs in one white editable highlight set with camera-scaled inset outlines.

[Quiet ordinary arrows](../_specspec/u8tHkaE=keep-ordinary-relationship-arrows-quiet-as-the-graph-is-zoomed-out.md)
keep the overview mesh subordinate to spotlight batches. [Neutral-ink scaling](../_specspec/yCYr-E0=scale-neutral-arrow-ink-from-seventy-to-thirty-five-percent-with-zoom.md)
chooses 70% theme neutral ink mixed with black from 70% scale and above, decreasing
linearly to 35% at 16% and below. Diff/draft colors and incident-hover emphasis remain independent;
minimum stroke/head geometry stays intact. The [shared canvas realization](../_specspec/asaRDK0=shared-graph-ui-implementation.md)
maps the pure, DOM and real-host paint checks.

## Persistent local spotlights and the owner backchannel

[Owner/agent messages](../_specspec/DG-JpDc=temporary-node-label-border-preview.md) are
immutable local spotlights with one message and unique full node IDs.
[Comparison context](../_specspec/TaNM294=associate-a-spotlight-with-its-revision-comparison.md)
lets one message discuss added, deleted, changed and unchanged nodes. Explicit refs
pin commits; the implicit default follows fresh HEAD versus live workspace.
Selecting a record switches comparison before highlighting and framing available
target/deleted-base nodes. Missing IDs remain selected; drifted versions still ring.

[The sparse-summary choice](../_specspec/c2WCD6c=store-sparse-workspace-drift-summaries-beside-comparison-references.md)
records capture HEAD and SHA-256 checksums only for uncommitted added/modified
workspace nodes, plus null deletion markers. All dirty nodes contribute context,
including unselected ones; clean CRLF/filtered checkouts remain clean under Git's
assessment. Committed node text stays in Git. [Local storage](../_specspec/P2i_png=keep-immutable-annotation-shots-in-a-checkout-local-store.md)
holds bounded metadata-only format-2 JSON in `.specspec-local/annotations`, shared
by both hosts until explicit reviewed flush. Older local records are protected
with a deliberate-flush diagnostic. Canonical node format/API remain 6.
[Identity resolution](../_specspec/63jO49Q=resolve-annotation-references-against-exact-snapshot-bytes.md)
derives current status/title/path and advisory drift/context warnings.

[The list](../_specspec/rvz48KY=integrate-arrivals-into-an-inspectable-annotation-list-without-interruption.md)
has one newest-first entry per message, with time/comparison/count. Its round red
badge counts new records since opening; initial/reload baselines are zero. Arrivals
preserve focus/caret, drafts, camera, selection, dropdown choice and old entries.
Independent watching includes historical views. [CLI parsing](../_specspec/rQTg56g=parse-spotlight-arguments-by-named-colors-and-canonical-ids.md)
takes IDs then a message with --base/--target; show reports A/M/D/R/= and warnings.

[The owner backchannel](../_specspec/7UOmpHw=send-owner-intent-back-to-agents-through-editable-highlights.md)
uses Shift-click to toggle one white ink, with Ctrl/Command+Shift removal and
whole-set clear. Change --spotlight-color in shared graph.css to try another ink.
[Capture](../_specspec/RY5LFw8=capture-one-version-aware-per-view-highlight-set.md)
saves IDs/message and the current comparison, including trusted native overlays
without saving documents or managed drafts. [Backend realization](../_specspec/n-Bk32Q=implement-immutable-local-shots-and-derived-snapshot-blob-identities.md)
and [shared host/UI realization](../_specspec/JTezmL0=transient-node-label-preview-implementation.md)
map code and bounded verification. [The spotlight guide](spotlights.md) explains
structures, CLI output, warning/fallback semantics and storage. Native controls
keep modified clicks. Physical Mac modifier behavior remains unverified.

[Type shapes](../_specspec/AZbsoEA=type-radii-and-content-fitting-circular-manifesto.md)
are Implementation **0px**, Requirement **24px**, and a true manifesto circle.
Ordinary compact cards are 264×112; ordinary expanded width is 860. Compact root is
264×264; expanded diameter is `ceil(hypot(822, intrinsicHeight)+48)` around the same
native editor. Actual outline ports retain 3-unit clearance and middle-40% circle
attachments. [Shape realization](../_specspec/YHSK9DA=type-roundness-and-circular-manifesto-implementation.md)
and [palette realization](../_specspec/Flf59Uc=rainbow-and-revision-colors-implementation.md)
link the corresponding tests.

## Separate palette playground

The [offline/export choice](../_specspec/IAy2dGI=offline-oklch-playground-and-copyable-palette.md)
implements the [interactive palette intention](../_specspec/XLyy460=standalone-rainbow-parameter-playground.md).
Open [`tools/rainbow-playground/index.html`](../tools/rainbow-playground/index.html)
directly. Defaults are seven colors, L=.69/C=.12, hue 320→20. Added selects near the
fixed green-text hue 149.5°, then Requirement takes the unused entry nearest 165°
with reuse fallback/earlier ties. Export JSON/CSS; clipboard rejection selects text.
This is a development tool, distinct from the maintained product examples.

## Maintained examples and history

**Gantt is the sole maintained product example.** It has its own current 22-node
graph and a complete independent [bundle/history walkthrough](../example/gantt/history/WALKTHROUGH.md).
Portfolio, personal manual-date and workshop forecast directions provide three
spec/code pairs with two substantial redirects. Each retained stage uses positive
binding text and current schema; Git carries redirect reasons and predecessor states.
Actual current CLI outputs form the receipts, and staged code trees retain anchors.

[Example policy](../_specspec/TAvql3w=independent-example-repository-policy.md)
and [bundle conclusion](../_specspec/YaXJpGE=independent-current-schema-gantt-history.md)
keep rigorous temporal tests independent of SpecSpec development schemas. Every node-
schema change refreshes **all** maintained example revisions/refs, receipts, ledger,
bundle and snapshot. Root development commits retain their original history.

The tracked `example/gantt` folder is a fixture snapshot in this Git worktree.
For an actual independent workspace:

```sh
python example/gantt/history/checkout.py ../specspec-examples/gantt-current
```

[The checkout choice](../_specspec/83D9YWw=external-example-checkouts.md) refuses
existing/development-worktree destinations and preserves partial/experimental clones.
Serious Git/host/app tests use the complete bundle; small generated graphs are focused
unit fixtures. Optional [STORY.md](../example/gantt/STORY.md) supplies labeled illustration.

## Engineering artifacts and checks

The [architecture Markdown](architecture.md) and [offline SVG](architecture.svg)
describe runtime boundaries and link the binding graph. [Its documentation choice](../_specspec/yJnnDfM=describe-runtime-boundaries-in-an-offline-engineering-map.md)
keeps the map descriptive. [Original asset/local-state policy](../_specspec/1aSOZOs=version-original-artwork-and-keep-generated-settings-local.md)
versions supplied artwork byte-for-byte, preserves generated local settings and
tracks shared launch files. Diagnostics, backups and experiments stay available.

Use the installed CLI or development Python; this checkout already has a graph:

```sh
python -m specspec show
python -m specspec query
python -m specspec context <full-id>
python -m specspec show <full-id> --dependents
python -m specspec update <full-id> --body <body-file>
python -m specspec delete <full-id> --dry-run --json
python -m specspec check --warnings-as-errors
python -m specspec check --staged --sources
python -m specspec --root example/gantt check --staged --sources
python example/gantt/history/verify.py --history
```

Read [AGENTS.md](../AGENTS.md) for all checks and phase guidance. Before each authorized
commit, validate both exact intended indexes. Run/diff evidence and failure rationale
belong in Git and preserved diagnostics. [Working validation](../_specspec/evfMtUM=continuous-self-validation.md)
and [real-host fixture/budget choices](../_specspec/PfJv45U=align-vscode-smoke-budget-with-existing-phase-guards.md)
state their bounded verification scope. [Complete Windows smoke evidence](investigations/host-smoke.md)
records measured shared/native/reload allowances and successful installed-host runs.
Semantic correctness, every-platform behavior,
filesystem races, watcher delivery and runtime performance require their own assessment.

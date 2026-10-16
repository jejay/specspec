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

## Compact command and shared-read contract

[Compact command intention](../_specspec/0dvOn3A=compact-useful-command-interface.md)
leads the [eight-command vocabulary](../_specspec/7tMgRa8=eight-everyday-commands-and-focused-advanced-tools.md),
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
controls. Native text rasterizes at the current scale; routes retain low-zoom stroke/
head strength and tangent joins. [Canvas rationale](node-canvas.md) describes the seams.

## Exact palette, hover and node shapes

[Seven swatches](../_specspec/gfAxHps=user-selected-seven-color-palette.md) are
`#bc82c9`, `#7e97e6`, `#1facce`, `#37b390`, `#92a64b`, `#ca8d3e`, `#dc7b7c`.
[Role intention](../_specspec/B87C_kI=added-green-first-and-leftover-requirement.md)
and [shared-table choice](../_specspec/6QB9hRY=shared-rainbow-table-and-derived-revision-fills.md)
map zero-based Requirement 4, Implementation 0, Added 3, M/R 1, D 6 and source-only 5.
One hop starts the table; distance repeats every seven. Revision mode colors the
manifesto too; distance/type keep its gray accent.

[Influence colors](../_specspec/zOX2L9c=color-absolute-and-relative-influence-continuously.md)
count unique descendants at all depths. The [normalization choice](../_specspec/JVHv1gc=normalize-revision-local-influence-on-a-continuous-warm-ramp.md)
uses zero to the highest non-manifesto count for Absolute influence, and cohort
minimum to maximum for Relative influence, grouping by **maximum** manifesto
distance. [Linear and logarithmic choices](../_specspec/HlpFtiA=keep-linear-and-logarithmic-influence-choices-together.md)
remain available together. Log Absolute Influence uses `log1p(c)/log1p(M)`;
Log Relative Influence uses `(log1p(c)-log1p(lo))/(log1p(hi)-log1p(lo))`, transforming
raw counts before subtracting the cohort minimum. The +1 defines zero without
changing the raw descendant count. All four modes share a continuous green `#4df884` → yellow `#e8d62c` → red `#ba2208` sRGB
ramp is separate from the seven swatches. Tied groups use green; the manifesto
stays gray. Full target/base revisions determine scales, never visible subsets.
[The influence realization](../_specspec/8Slagkc=render-continuous-absolute-and-cohort-relative-influence.md)
maps lazy metric ranges, compact/expanded paint, gradient legends and verification.

Cards use shared 15% resting/24% hover tint and ordinary theme text.
[Hue-emphasizing hover](../_specspec/bLBNk80=hue-preserving-hover-lightness-and-chroma.md)
increases colored border/incident ink lightness and chroma. The neutral manifesto's
hover border is white. [Immediate-context darkening](../_specspec/6MUwTIw=stable-root-and-transient-hover-darkening.md)
is transient and preserves geometry/native forms. [Spotlight rings](../_specspec/E7O_6GU=view-local-label-cycle-with-inset-border.md)
paint exact versions in one editable colored highlight set with an 8px inset outline.

[Quiet ordinary arrows](../_specspec/u8tHkaE=keep-ordinary-relationship-arrows-quiet-as-the-graph-is-zoomed-out.md)
keep the overview mesh subordinate to spotlight batches. [Neutral-ink scaling](../_specspec/yCYr-E0=scale-neutral-arrow-ink-from-seventy-to-thirty-five-percent-with-zoom.md)
chooses 70% theme neutral ink mixed with black at actual size, decreasing linearly
to 35% at 12% zoom. Diff/draft colors and incident-hover emphasis remain independent;
minimum stroke/head geometry stays intact. The [shared canvas realization](../_specspec/asaRDK0=shared-graph-ui-implementation.md)
maps the pure, DOM and real-host paint checks.

## Persistent local spotlights and the owner backchannel

[Agent answers](../_specspec/DG-JpDc=temporary-node-label-border-preview.md) are immutable
spotlights, each one message with colored node/version sets. The [local-store
choice](../_specspec/P2i_png=keep-immutable-annotation-shots-in-a-checkout-local-store.md)
keeps shot files and exact retained node bytes in `.specspec-local/annotations`,
Git-excluded and shared by both hosts for the same checkout until explicit flush.
[Version resolution](../_specspec/63jO49Q=resolve-annotation-references-against-exact-snapshot-bytes.md)
uses full node IDs and exact SHA-1/SHA-256 Git blob addresses against actual saved,
native-overlay or selected revision bytes. Canonical node format is 6.

[Attention and list integration](../_specspec/rvz48KY=integrate-arrivals-into-an-inspectable-annotation-list-without-interruption.md)
use a round red toolbar badge counting only new batches since this view last opened
its dropdown. Existing entries establish a zero-count baseline; opening clears the
count, and reload starts a new in-memory baseline. The anchored newest-first dropdown
has one text entry per spotlight. Selection activates all its colored sets, closes
the menu and frames the exact matching union in the full canvas, retaining drafts.
Compact version counts replace member/detail/preview UI. Arrivals retain editing,
focus, camera, selection and older spotlights. Independent watching works in historical views too. [Storage/identity realization](../_specspec/n-Bk32Q=implement-immutable-local-shots-and-derived-snapshot-blob-identities.md)
and [shared UI/host realization](../_specspec/JTezmL0=transient-node-label-preview-implementation.md)
map code and verification seams. The [spotlight guide](spotlights.md) gives the
`spotlight add/show/flush` contract, storage/lifetime limits and verification scope.
[Argument parsing](../_specspec/rQTg56g=parse-spotlight-arguments-by-named-colors-and-canonical-ids.md)
recognizes named colors and full IDs before the shared message, uses purple for
initial uncolored IDs and rejects duplicate members.
Public naming is independent of internal store/transport keys; retained immutable
submissions keep their original bytes.

[The owner backchannel](../_specspec/7UOmpHw=send-owner-intent-back-to-agents-through-editable-highlights.md)
unifies manual and spotlight-applied highlights. Shift-click node chrome cycles
red/blue/green/purple/turquoise/yellow/off; Ctrl+Shift or macOS Command+Shift removes
one member. Clear highlight removes the set. The dropdown can save it with a
message as a new immutable spotlight for `spotlight show` to expose to the agent.
[Version-aware capture](../_specspec/RY5LFw8=capture-one-version-aware-per-view-highlight-set.md)
keeps exact references as per-view state and resolves retained, target/base and
trusted native-overlay bytes atomically. Creation preserves forms/camera and uses
highlights provenance for possibly mixed revisions; originals stay immutable.
Native controls keep their modified clicks. Mac event handling is covered
synthetically only; actual Mac host behavior remains unverified.

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

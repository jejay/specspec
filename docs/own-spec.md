# SpecSpec's current specification

[`.specspec/`](../.specspec/) is this repository's binding current graph. It describes
owner intentions, separately reasoned conclusions and actual implementation mappings.
Git predecessor trees and commit messages retain changed decisions and run evidence.
[`INTENTION_SPEC.md`](../INTENTION_SPEC.md) preserves the original owner input;
[`CONCLUSION_SPEC.md`](../CONCLUSION_SPEC.md) summarizes current technical choices.

## Planning process

The owner's preliminary process in [AGENTS.md](../AGENTS.md) is represented by:

| Element | Node |
| --- | --- |
| Implementation-mature spectrum planning | [r1wddEQ=](../.specspec/r1wddEQ=.md) |
| Positive current binding text | [LjbEgSo=](../.specspec/LjbEgSo=.md) |
| Inspect/preserve owner changes | [MPOzb8A=](../.specspec/MPOzb8A=.md) |
| Tandem understanding and choice review | [93sqYPw=](../.specspec/93sqYPw=.md) |
| Agent planning and separate specification commits | [FU5NaYc=](../.specspec/FU5NaYc=.md) |
| Depth-focused implementation and conflict reporting | [kvBgyYw=](../.specspec/kvBgyYw=.md) |

Owner planning may supply direct edits. Tandem planning discusses intentions and
meaningful choices while leaving manipulation to requested agent planning. Agent
planning preserves owner input first, deepens/reconciles the graph through CLI
operations, checks the exact index and commits an agent changeset. Implementation
adds depth under established intentions and communicates conflicts/subset choices;
scope changes return to owner planning. These are agent working instructions, while
product CLI/UI staging and commits remain controlled by their users.

Precision aims at faithful implementation. Review and evidence still assess meaning
and uncertainty; the graph's position is a justification relationship. The
[review intention](../.specspec/3wsnEjk=.md) follows the
owner's uncertainty/impact/token budget. [Revisable conclusions](../.specspec/VZvwDBY=.md)
keep solution choices independently addressable.

## Product grammar and canonical data

The [manifesto](../.specspec/XV5_rPQ=.md) leads a
[rooted DAG](../.specspec/DiIJxaQ=.md) of requirements and
terminal implementation leaves. [Spectrum position](../.specspec/W8_8BXA=.md)
follows relationships. The flat `.specspec` directory contains direct node Markdown
files; frontmatter holds identity/type/parents and the body holds binding text.

[Compact identity](../.specspec/F5JaC_4=.md) and the
[typed schema conclusion](../.specspec/qowy5AI=.md)
choose padded RFC 4648 Base64url over five random bytes: **40 bits**, seven payload
symbols and the full trailing `=`. Filename form: `<id>.md`. Lock-scoped
creation retries exact/casefold collisions; validation checks portable aliases.
The [ID-only path choice](../.specspec/ezHjLDs=.md) keeps filenames independent of
binding text across CLI creation, native editors and every maintained example revision.
Its [realization](../.specspec/OfBdhms=.md) maps exact path validation, creation forms,
editor discovery and the reconstructed history to code and regression checks.
Current **node format 7** defines the sole supported node scheme; **API 7** defines the compact application protocol. Schema errors and
unsupported historical formats receive diagnostics. Source blob IDs address code
contents; transaction protection compares original bytes.

[Shortcut-free justifications](../.specspec/uAjln2M=.md)
require each direct parent to contribute ancestry. The
[shared validation choice](../.specspec/pA2ls_g=.md)
checks all candidates, native overlays, historical graphs and exact indexes under
one current contract, reporting alternative paths without repairing edges. Ancestor
bindings carry justification; implementations contribute bounded realizations.
Review ripple effects using both old and new graphs. See [graph structure](graph-structure.md).

[Managed transactions](../.specspec/6SyZ-BU=.md)
diagnose saved/candidate graphs and journal explicit bytes/null deletions under a lock in
`.specspec-local`. Recovery recognizes known original/replacement/absence states
and preserves intervening external text. Retain interruption state and use
`recover`; clear stale locks only after confirming the writer absent.

## Exact deletion, invalid working graphs and HEAD views

[Deletion/HEAD intention](../.specspec/xu6W0c4=.md),
[descendant intention](../.specspec/fuyy0Lk=.md),
[ghost conclusion](../.specspec/5d5oDCM=.md)
and [plan/warning conclusion](../.specspec/AuhoBoU=.md)
separate explicit deletion from potential reasoning effects. Managed deletion removes
exactly selected files; surviving conclusions retain all declarations, including missing
parents. Preview reports selected uncommitted files, retained faults and potential
scope. Warned noninteractive deletion requires `--yes`; hosts confirm the reviewed
plan under lock. See [deletion commands](deletion.md) and [invalid-state repair](invalid-graphs.md).

[Invalid-state intention](../.specspec/-RQn7Ug=.md) separates operation success,
structural validity and potential semantic effects. [Inspection/context](../.specspec/L5Xamn4=.md)
provides raw/working/historical reads, issue selection and contextual diffs.
[Explicit authoring](../.specspec/0piRXe0=.md) permits individual or composed
editing steps with optional complete `--require-valid`. [Fresh host context](../.specspec/PAkzXxk=.md)
keeps broken relationships visible and safe current forms editable.
[Native repair fields](../.specspec/qSK7qA0=.md) preserve actual empty/source-JSON
input separately from canonical membership.
[Realization](../.specspec/U3s4seg=.md) links shared backend/host code and verification.

Default workspace views reread HEAD. Committed deleted nodes remain copyable,
read-only D ghosts through staging and disappear after commit. Historical comparisons
retain independent views. File/Git watchers provide bounded event hints, with explicit
Refresh/optional polling (default off). Native Delete requires clean project documents.
[Ghost implementation](../.specspec/JqNzSPg=.md)
and [exact-deletion implementation](../.specspec/huB7hcg=.md)
map the current code and regression seams.

## Source regions and Git consistency

[Source-region intention](../.specspec/v6xn2GU=.md),
[blob choice](../.specspec/jsIUeP0=.md)
and [tracking contract](../.specspec/VnSF9BE=.md)
use project-relative paths, full immutable SHA-1/SHA-256 blobs and multiple inclusive
ranges. Strict reports internal changes; expanding absorbs internal/contained changes.
Both exclude outer-boundary insertions and gaps. Ambiguity, deletion, unavailable
objects and mapping budgets remain explicit. Git trees retain anchor objects.

[Implementation](../.specspec/vQFml0Y=.md)
links its own strict schema and expanding resolver/command anchors. Whole-file hints
remain usable. [The source guide](source-regions.md) documents inspection/capture/check/
reanchor, literal previews, retention and limits. Capture uses the existing
native or managed form's save owner. File-level source impact stays conservative.

[Exact-index and revision reasoning](../.specspec/Yfy0414=.md)
checks staged blobs and compares full IDs/edges/sources without checkout.
Owner-configured hooks/CI call `check --staged`; adding `--sources` assesses staged
code mapping/retention. Hook files and Git operations remain under owner control.

## Shared host experience

[One renderer/session](../.specspec/YOPhqYc=.md) and a
[Python domain library/CLI](../.specspec/LvYBN_4=.md)
serve VS Code and Electron. [Native documents](../.specspec/GQdmCrA=.md)
open equals-delimited node files in the main editor with raw-text access, split
TextDocument synchronization and independent view cameras. Python plans; native
Save/autosave/undo/recovery persist documents. Invalid text remains repairable.
Electron/project actions use the managed writer. [Watch reconciliation](../.specspec/tvic3PQ=.md)
retains drafts/caret/cameras while publishing fresh diagnosable graphs; unavailable
loads retain marked last-usable views.

[Electron isolation](../.specspec/3SfTeOo=.md)
constrains preload/IPC/assets and authorizes local projects with trusted launch
settings. Python/Git are external prerequisites. [Agent connectors](../.specspec/3FThKz4=.md)
are separately scoped future transport/authorization work.

## Remote workspaces and prompt loading

[Remote intention](../.specspec/CmZafVM=.md) and
[workspace-host boundaries](../.specspec/uY3KPsM=.md)
place the Node/Python/Git adapter beside real local or remote project files while
VS Code owns transport and client rendering. See [remote setup/qualification](remote-workspaces.md).

[Loading intention](../.specspec/tGpRMLM=.md) is
refined by [Git batching](../.specspec/wAp9Qz8=.md),
[shared/bootstrap reads](../.specspec/3V6SdSA=.md),
[derived caches](../.specspec/L0KGXB8=.md),
[working-first comparison](../.specspec/VDss3KM=.md)
and [measurement scope](../.specspec/FJj-9xY=.md).
[Loading diagnostics](loading.md) explain current controls and cache safeguards;
[investigations](investigations/vscode-loading.md) retain the motivating evidence.
[Backend realization](../.specspec/FhVjOvo=.md)
and [workspace/phased-host realization](../.specspec/N7IR7Fw=.md)
map the code, diagnostic controls and verification seams.
[Superseded-read handling](../.specspec/KGvVHh0=.md)
keeps generation/text races distinct from invalid files, coalescing bounded fresh
attempts while preserving the displayed presentation and mutation preflights.
[Project-scoped API channels](../.specspec/sxxzsrk=.md)
reuse interpreter lifetime with a separate read-only preview channel. Each request
still validates fresh files and Git state. [Interactive source reads](../.specspec/TpFMeZc=.md)
bind to the published view and displayed commit, while [metadata events](../.specspec/0aNDHfQ=.md)
and [HEAD/ref watching](../.specspec/yEoFkOE=.md)
coalesce their own work. The [implementation](../.specspec/HZHjxQ8=.md)
links channels, scheduling and causal/installed regressions.
The [polling lifecycle verification choice](../.specspec/wkCbtnQ=.md)
separates periodic ticks from still-valid watcher hints and pending work.
[Its causal investigation](investigations/polling-test-race.md) reproduces the late
initial-discovery race and verifies shutdown/disposal with controlled clocks.

## Compact command and shared-read contract

[Compact command intention](../.specspec/0dvOn3A=.md)
leads the [everyday command vocabulary](../.specspec/7tMgRa8=.md),
[readable defaults](../.specspec/sJ5dyh4=.md),
[full review diffs](../.specspec/7kYVG_E=.md)
and [compact API 7](../.specspec/cpFRqIM=.md).
Canonical node format is **7**. The [shared read path](../.specspec/-UedVEw=.md)
serves both hosts with optional native overlays; [safeguards](../.specspec/nIj9fmE=.md)
and [coordinated examples/cutover](../.specspec/4ZvnSGw=.md)
retain their domain and verification boundaries. The [command guide](cli.md) gives
current operational recipes; original owner source remains unchanged in AGENTS.md.
[Direct authoring](../.specspec/rgGL5FY=.md) supplies bodies and batches through
arguments. The [message choice](../.specspec/BKekD_o=.md) exposes repeatable
`-m/--message`, with explicit hidden bulk body inputs separate from literal text.
[One editing vocabulary](../.specspec/pRK4Qwk=.md) and the
[chain grammar](../.specspec/4626uI8=.md) combine add/update/delete steps into one
candidate, consent decision and recovery scope, with `--as` / `$name` parent aliases
and forward references. Other commands stay standalone. The
[message realization](../.specspec/Fy-_P9A=.md) maps literal body input and unchanged
UI transports. Node format and API remain 7; OS argument limits remain distinct from
bulk input limits. [Message transport evidence](investigations/argument-authoring.md)
and [chain verification](investigations/editing-chains.md) record the boundaries and
current-history reconstruction. [Chain implementation](../.specspec/kdTk6-0=.md)
maps complete preflight, shared transactions and alias receipts to code and tests.
[Selected-passage edits](../.specspec/kiRE62k=.md) and the
[exact replacement choice](../.specspec/1GJRSPU=.md) add repeatable
`update --replace OLD NEW` as an alternative to full-body input. Unique, disjoint
matches on the fresh original body retain unrelated text; every step shares the
same candidate and recovery boundary. [Realization](../.specspec/O0xeA4Y=.md) links
the matcher, preflight and existing writer. The [default layout choice](../.specspec/EcEFfgg=.md)
tolerates line endings and source-mapped prose soft breaks while preserving Markdown
structure, all-layout uniqueness and literal NEW. It adds no matching options.
[Replacement evidence](investigations/exact-replacements.md) records parser/work
bounds, original source mapping, stale-match rejection and verification scope.
[One inspection vocabulary](../.specspec/2FfVd-Y=.md) and
[query consolidation](../.specspec/aILBxDs=.md) put parsed bindings, descendants and
raw repair reads under query. [Understandable help](../.specspec/DOqGIio=.md) and
[task guides](../.specspec/ivvUgP4=.md) explain arguments, defaults, examples and
safety in every help output. [Evidence](investigations/cli-help.md) records the
host preflight and maintained-history coordination.
[CLI/review implementation](../.specspec/SF12qpA=.md)
and [shared host implementation](../.specspec/GG_koyg=.md)
map the code and verification seams.

[Complete tree-shaped reads](../.specspec/kiOMI7I=.md)
serve human and agent readers with complete revision comparisons. The
[last-occurrence choice](../.specspec/T693TDw=.md)
orders selected-record projections through iterative reverse/forward DFS. The
[compact-header choice](../.specspec/nLqvWcM=.md)
keeps two-column rails and every direct parent in full headers. The
[comparison choice](../.specspec/h3zqGZU=.md)
uses spotlight-style HEAD/workspace defaults, complete current/base binding content
and sparse worded change hints. The [default one-line choice](../.specspec/AY1g-sU=.md)
joins single newlines with a space and longer runs with ` ¶ `; JSON preserves logical
body layout with CRLF normalized to LF, while raw query/diff retains physical bytes. The [compact/human presentation choice](../.specspec/B6y6hgo=.md)
groups sources into one comma-separated line by default; `--human` keeps logical
body lines and lists sources individually. Parent IDs always use comma-space
separators. Both modes retain the same facts and JSON. Lowercase type/status words
make the legend unnecessary, and root content aligns with its header. The [selected-record overlay](../.specspec/B71bAFk=.md)
keeps deleted records among current records, selecting former parents only for
deleted nodes. Valid revisions yield an acyclic projection; invalid current
references use cycle-safe component readings and missing endpoints. Original
revision graphs remain reconstructible. Normal records stay unmarked; exact text changes belong to `diff`.
The [source comparison choice](../.specspec/jWl96h0=.md)
separates reference-list changes, conservative linked-file impact, selected code
text and actual per-version locations under shared strict/expanding resolution.
The [contract-aware query choice](../.specspec/z9YKFeE=.md)
keeps changes permitted by strict/expanding/path-only references quiet, including
source-changed badges. Known contract transitions propagate through both original graphs. One-line
sources retain broken/uncertain/restored hints; JSON keeps complete raw source facts
and separate contract classifications. Shared file-impact reporting stays broader.
The [per-invocation batch choice](../.specspec/2doGbqA=.md)
loads known committed source blobs and anchors into the existing per-call cache,
while refs/workspace files remain fresh. [Profiling evidence](investigations/query-performance.md)
includes fixed-input equality, subprocess-count regressions and reproducible timings.
[Implementation](../.specspec/Kxh7M4Q=.md)
maps the renderer, source reader integration, CLI, plain-output golden cases and
independent temporal/structure checks. [Rooted subgraph selection](../.specspec/rt-nZHM=.md)
adds minimum/maximum distance and highest-first self-inclusive influence criteria.
The [cutoff choice](../.specspec/8O0LYEM=.md)
uses inclusive integers or exact ceil-percentage quotas on one rooted population,
ID tie-breaks and independent subquery unions. The [batch choice](../.specspec/YkxeXd0=.md)
shares distance propagation and reverse influence bitsets, releases consumed masks,
and limits code resolution to necessary original-graph evidence. Scoped JSON keeps
complete selected bindings, external parent IDs and source provenance. See
[the query guide](query.md). The [ancestor completion choice](../.specspec/-fXS-dI=.md)
adds every matched record's parents after selection, distinguishes additional
bindings from quota matches and lists omitted nearby IDs without their bodies.
The query emitter formats once and supports an exact encoded byte budget. The
same query pipeline supplies complete agent context; the current everyday surface
has seven verbs. Current-command receipts, source anchors and all retained Gantt
refs are reconstructed together. Node format is 7; API is 7.

## Header identity and keyboard saving

[Selected identity](../.specspec/4PzVJho=.md), the
[optical-asset choice](../.specspec/ALlkmT0=.md) and
[asset realization](../.specspec/Aq02oUE=.md) import the final Spectrum flow symbol
and launcher tile locally. [Compact header context](../.specspec/EXGxivM=.md)
groups the accessible symbol with the live revision label, uses an icon-only
Refresh action and keeps project picking in VS Code's existing command while
Electron retains its visible picker/menu. Below it, legends and diagnostics retain
their space; linked source-file totals/list remain in CLI reports, with graph-node
source cues preserved by the [Git-cue choice](../.specspec/fdB9ZLM=.md).
[Keyboard saving](../.specspec/-DClehg=.md)
submits focused forms with Ctrl/Command+S through their existing Save owner and
restrictions. [Realization](../.specspec/tyygZV8=.md) maps shell, renderer, typed
adapter and verification. [Branding provenance](../branding/README.md) preserves
original owner artwork and records the selected imports independently of graph colors.

## Neighborhood UI revision

[Focused editing](../.specspec/t8RQMdE=.md) expands the same native
form within compact direct parents/children. [Inline changes](../.specspec/6Bk988A=.md)
keep original and edited binding text together. The [shared control choice](../.specspec/ZacVi3g=.md)
uses a locally bundled CodeMirror unified diff in both VS Code and Electron,
retaining each host's save/undo owner; [its realization](../.specspec/bQscaSo=.md)
maps target-only edits, themed change blocks and unit/installed-host checks.
Actual links and candidate parents are separate; child counts include unique
all-depth descendants. [Path bounds](../.specspec/FHfnj08=.md)
use full individual revisions, while [neighborhood context](../.specspec/V0xi_J8=.md)
keeps potential impact understandable. Counts and distances are derived presentation.

[Relational world layout](../.specspec/LtROyww=.md)
uses left-to-right earliest ranks and a deterministic compact backbone while drawing
every relationship. [Dagre/D3](../.specspec/tgHQyx4=.md)
are locally bundled. [Spatial navigation](../.specspec/mAZgRy8=.md)
uses 12–250% pointer-anchored zoom and unconstrained pan with explicit frame/100%
controls. [Floating controls](../.specspec/FZO2_-Q=.md)
keep framing icons over the full canvas. [Rectangle framing](../.specspec/zs0OtME=.md)
uses the [captured-pointer choice](../.specspec/zwevPEc=.md):
Ctrl on Windows/Linux, Command on Mac, a latched drag through modifier release,
and framing on pointer release. Cancellation clears the transient tool. Native
text rasterizes at the current scale; routes retain low-zoom stroke/head strength
and tangent joins. [Canvas tutorial](node-canvas.md#canvas-controls) describes the gestures.

## Exact palette, hover and node shapes

[Seven swatches](../.specspec/gfAxHps=.md) are
`#bc82c9`, `#7e97e6`, `#1facce`, `#37b390`, `#92a64b`, `#ca8d3e`, `#dc7b7c`.
[Role intention](../.specspec/B87C_kI=.md)
and [shared-table choice](../.specspec/6QB9hRY=.md)
map zero-based Requirement 4, Implementation 0, Added 3, M 1, D 6 and source-only 5.
One hop starts the table; distance repeats every seven. Revision mode colors the
manifesto too; distance/type keep its gray accent.

[Influence colors](../.specspec/zOX2L9c=.md)
count self plus unique descendants at all depths, with a minimum of one. The
[normalization choice](../.specspec/JVHv1gc=.md)
uses `(c-1)/(M-1)` for Absolute influence, and cohort minimum to maximum for
Relative influence, grouping by **maximum** manifesto distance.
[Linear and logarithmic choices](../.specspec/HlpFtiA=.md)
remain available together. Log Absolute Influence uses `log(c)/log(M)`;
Log Relative Influence uses `(log(c)-log(lo))/(log(hi)-log(lo))`, transforming
self-inclusive counts before subtracting the cohort minimum. Structural downstream
counts exclude self. All four modes share a continuous green `#4df884` → yellow `#e8d62c` → red `#ba2208` sRGB
ramp, separate from the seven swatches. Tied groups use green; the manifesto
stays gray. Full target/base revisions determine scales, never visible subsets.
[The influence realization](../.specspec/8Slagkc=.md)
maps lazy metric ranges, compact/expanded paint, gradient legends and verification.

Cards use shared 15% resting/24% hover tint at actual size and ordinary theme text.
[Overview shapes](../.specspec/sV3uzvQ=.md)
progressively fill to their painted borders as zoom decreases. The
[two-stage mixing choice](../.specspec/eqWEPJI=.md)
starts fill progression at 40% scale and reaches the painted border at 16%, separately
from ordinary arrows' 70%-to-16% quieting interval. Exact actual-size tints remain.
[Positive concise copy](../.specspec/iHpAyAE=.md)
keeps legends to actual color labels, with tutorials in documentation. Its
[realization](../.specspec/znpy2MA=.md)
covers shared UI, host repair text and the palette playground.
[Hue-emphasizing hover](../.specspec/bLBNk80=.md)
increases colored border/incident ink lightness and chroma. The neutral manifesto's
hover border is white. [Immediate-context darkening](../.specspec/6MUwTIw=.md)
is transient and preserves geometry/native forms. [Spotlight rings](../.specspec/E7O_6GU=.md)
paint available selected IDs in one white editable highlight set with camera-scaled inset outlines.

[Quiet ordinary arrows](../.specspec/u8tHkaE=.md)
keep the overview mesh subordinate to spotlight batches. [Neutral-ink scaling](../.specspec/yCYr-E0=.md)
chooses 70% theme neutral ink mixed with black from 70% scale and above, decreasing
linearly to 35% at 16% and below. Diff/draft colors and incident-hover emphasis remain independent;
minimum stroke/head geometry stays intact. The [shared canvas realization](../.specspec/asaRDK0=.md)
maps the pure, DOM and real-host paint checks.

## Persistent local spotlights and the owner backchannel

[Owner/agent messages](../.specspec/DG-JpDc=.md) are
immutable local spotlights with one message and unique full node IDs.
[Comparison context](../.specspec/TaNM294=.md)
lets one message discuss added, deleted, changed and unchanged nodes. Explicit refs
pin commits; the implicit default follows fresh HEAD versus live workspace.
Selecting a record switches comparison before highlighting and framing available
target/deleted-base nodes. Missing IDs remain selected; drifted versions still ring.

[The sparse-summary choice](../.specspec/c2WCD6c=.md)
records capture HEAD and SHA-256 checksums only for uncommitted added/modified
workspace nodes, plus null deletion markers. All dirty nodes contribute context,
including unselected ones; clean CRLF/filtered checkouts remain clean under Git's
assessment. Committed node text stays in Git. [Local storage](../.specspec/P2i_png=.md)
holds bounded metadata-only format-2 JSON in `.specspec-local/annotations`, shared
by both hosts until explicit reviewed flush. Older local records are protected
with a deliberate-flush diagnostic. Canonical node format is 7; API is 7.
[Identity resolution](../.specspec/63jO49Q=.md)
derives current status/title/path and advisory drift/context warnings.

[The list](../.specspec/rvz48KY=.md)
has one newest-first entry per message, with time/comparison/count. Its round red
badge counts new records since opening; initial/reload baselines are zero. Arrivals
preserve focus/caret, drafts, camera, selection, dropdown choice and old entries.
Independent watching includes historical views. [CLI parsing](../.specspec/rQTg56g=.md)
takes IDs then a message with --base/--target; show reports A/M/D/= and warnings.

[The owner backchannel](../.specspec/7UOmpHw=.md)
uses Shift-click to toggle one white ink, with Ctrl/Command+Shift removal and
whole-set clear. Change --spotlight-color in shared graph.css to try another ink.
[Capture](../.specspec/RY5LFw8=.md)
saves IDs/message and the current comparison, including trusted native overlays
without saving documents or managed drafts. [Backend realization](../.specspec/n-Bk32Q=.md)
and [shared host/UI realization](../.specspec/JTezmL0=.md)
map code and bounded verification. [The spotlight guide](spotlights.md) explains
structures, CLI output, warning/fallback semantics and storage. Native controls
keep modified clicks. Physical Mac modifier behavior remains unverified.

[Type shapes](../.specspec/AZbsoEA=.md)
are Implementation **0px**, Requirement **24px**, and a true manifesto circle.
Ordinary compact cards are 264×112; ordinary expanded width is 860. Compact root is
264×264; expanded diameter is `ceil(hypot(822, intrinsicHeight)+48)` around the same
native editor. Actual outline ports retain 3-unit clearance and middle-40% circle
attachments. [Shape realization](../.specspec/YHSK9DA=.md)
and [palette realization](../.specspec/Flf59Uc=.md)
link the corresponding tests.

## Separate palette playground

The [offline/export choice](../.specspec/IAy2dGI=.md)
implements the [interactive palette intention](../.specspec/XLyy460=.md).
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

[Example policy](../.specspec/TAvql3w=.md)
and [bundle conclusion](../.specspec/YaXJpGE=.md)
keep rigorous temporal tests independent of SpecSpec development schemas. Every node-
schema change refreshes **all** maintained example revisions/refs, receipts, ledger,
bundle and snapshot. Root development commits retain their original history.

The tracked `example/gantt` folder is a fixture snapshot in this Git worktree.
For an actual independent workspace:

```sh
python example/gantt/history/checkout.py ../specspec-examples/gantt-current
```

[The checkout choice](../.specspec/83D9YWw=.md) refuses
existing/development-worktree destinations and preserves partial/experimental clones.
Serious Git/host/app tests use the complete bundle; small generated graphs are focused
unit fixtures. Optional [STORY.md](../example/gantt/STORY.md) supplies labeled illustration.

## Local 0.1 delivery and project guidance

The [initial release intention](../.specspec/1T-fMcs=.md) covers a global isolated
CLI, a locally installed VSIX and portable desktop delivery from one monorepo.
[Private workspace packaging](../.specspec/DFS2oJM=.md) keeps Python separate from
one locked npm workspace, with root build/test/package commands and inspected
artifacts rather than implicit publication. [Project guide intention](../.specspec/1zcoS-g=.md)
and [initialization ownership](../.specspec/J8H7P74=.md) supply a package-resource
AGENTS.md only when absent, with explicit byte-checked recovery and preserved owner
instructions. See [agent guidance](agents.md) and [installation](install.md).

The [introduction intention](../.specspec/U6paNqA=.md) and
[selected presentation choice](../.specspec/1ev9uZo=.md) lead the README with the
reasoning problem, revisable choices and exact brand assets before setup detail.
The [directory choice](../.specspec/79zOr-w=.md) coordinates the sole `.specspec/`
location across the backend, hosts and every maintained Gantt revision. Original
owner input remains archival, while current guides use the installed global command.
[Pinned-dependency scope](../.specspec/Q7FDb7A=.md) separates local packaging from
unqualified publishing authentication. [Logical versus physical readings](../.specspec/MmfPuhY=.md)
make API-7 CRLF normalization explicit while raw documents preserve bytes.
[Release realization](../.specspec/przmxmo=.md) and
[guide realization](../.specspec/nxNOTwc=.md) map the packaging, documentation,
initialization and artifact-host verification. [Release procedure](releasing.md)
and [bounded evidence](investigations/release-0.1.md) distinguish builds,
actual installed-artifact qualification and future publication.

## Engineering artifacts and checks

The [architecture Markdown](architecture.md) and [offline SVG](architecture.svg)
describe runtime boundaries and link the binding graph. [Its documentation choice](../.specspec/yJnnDfM=.md)
keeps the map descriptive. [Original asset/local-state policy](../.specspec/1aSOZOs=.md)
versions supplied artwork byte-for-byte, preserves generated local settings and
tracks shared launch files. Diagnostics, backups and experiments stay available.

Use the installed CLI or development Python; this checkout already has a graph:

```sh
python -m specspec query
python -m specspec query <full-id> --max-distance 0 --with-ancestors
python -m specspec query <full-id>
python -m specspec update <full-id> -m "# Revised conclusion" -m "Current reasoning."
python -m specspec delete <full-id> --dry-run --json
python -m specspec check --warnings-as-errors
python -m specspec check --staged --sources
python -m specspec --root example/gantt check --staged --sources
python example/gantt/history/verify.py --history
```

Read [AGENTS.md](../AGENTS.md) for all checks and phase guidance. Before each authorized
commit, validate both exact intended indexes. Run/diff evidence and failure rationale
belong in Git and preserved diagnostics. [Working validation](../.specspec/evfMtUM=.md)
and [real-host fixture/budget choices](../.specspec/PfJv45U=.md)
state their bounded verification scope. [Complete Windows smoke evidence](investigations/host-smoke.md)
records measured shared/native/reload allowances and successful installed-host runs.
Semantic correctness, every-platform behavior,
filesystem races, watcher delivery and runtime performance require their own assessment.

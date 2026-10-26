# Current technical conclusions

The binding specification is the intention-conclusion graph in
[`.specspec/`](.specspec/). [Its tour](docs/own-spec.md) distinguishes owner outcomes,
reasoned implementation choices and actual realization links. This document summarizes
current choices. Git stores their evolution and execution evidence; the original
owner input remains in [`INTENTION_SPEC.md`](INTENTION_SPEC.md).

## Specification planning

[AGENTS.md](AGENTS.md) defines preliminary owner, tandem, agent-planning and
implementation phases. Inspect owner edits before action. Agent planning preserves
owner input in its own `Owner specspec changes:` commit, deepens the current positive
graph through tools, validates the intended index and commits `Agent specspec changes:`.
Tandem planning discusses consequential choices; implementation adds depth under
established intentions and reports contradictions/subset decisions to the owner.
The metaphorical compiler-level goal motivates precise contracts and independently
addressable choices, with human review assessing remaining uncertainty.

## Domain library, CLI and hosts

Use Python 3.11+, Hatchling, Click, ruamel.yaml, markdown-it-py and pytest. The importable domain
library and console/module CLI serve all hosts. Prefer global `uv tool install` or
`pipx install` isolation across projects, retain optional one-shot uvx, and support local/
Git installation; publication is separately authorized.

```text
src/specspec/
  model.py / format.py      # Current schema, diagnostics and targeted Markdown
  graph.py                 # Rooted DAG, deterministic order, iterative closures
  query.py                 # Plain current-state reads with sparse revision/source hints
  query_sources.py         # Declaration, byte, selected-text and location comparisons
  workspace.py             # Discovery, validated byte transactions and recovery
  deletion.py              # Descendant scope and uncommitted-file assessment
  git.py                   # Index/revision reads and semantic/source impact
  editor.py                # Non-writing native overlays and document plans
  source_schema.py         # Shared whole-file/region validation
  sources.py               # Bounded blob/range resolution and retention
  source_commands.py       # Inspect/capture/reanchor; deliberate source writes
  annotations.py           # Comparison spotlights and sparse workspace drift summaries
  annotation_commands.py   # Public spotlight add/show/flush
  application.py / wire.py # Shared reads/plans and compact comparison projection
  output.py / cli.py       # Readable review presentation and API-7 envelopes
  cli_help.py              # Task-oriented static help for every command/group
  replacement_matching.py  # Source-mapped newline/prose comparison
  body_replacements.py     # Disjoint original-body passages plus literal NEW
graph-ui-common/            # One DOM/SVG renderer, session, camera, build/template
vscode/                     # Document/project/view adapter and native facilities
electron/                   # Authorized main/preload/renderer and local storage
```

Adapters call the CLI with argument arrays, bounded UTF-8 stdin/output and a fixed
trusted executable. The Python library owns graph/schema/serialization rules.
API 7 structured stdout is one `{api_version, ok, result, diagnostics}` envelope; exit 0 means
success, 1 validation/rejected operation, 2 invocation/I/O failure. Diagnostics have
stable codes, severity, path/optional ID and actionable text. Ordinary bodies use
literal repeatable -m paragraphs; explicit integration --body FILE|- supplies UTF-8
files/stdin. Full-parent updates replace the supplied set. Repeated --replace OLD NEW
selects unique disjoint original passages with default line-ending/prose tolerance;
NEW and unselected text remain literal. Only add/update/delete compose into one
candidate, consent decision and recoverable transaction, with local parent aliases.

The [compact command guide](docs/cli.md) defines seven everyday verbs with readable
text/Markdown defaults and explicit compact JSON. Full review diffs show all canonical
file hunks, semantic node/relationship changes and separate linked-source impact.
Comparison transport shares unchanged records; both hosts use the same read coordinator
with optional native overlays and working-first loading. Native persistence stays
separate from managed writes. Node format and protocol are **7**. Detailed static
--help explains every root/command/subgroup purpose, inputs, defaults, examples and
safety; ordinary result verbosity stays independent. Query is the specification
inspection vocabulary. Raw query reads saved, exact-index or committed documents
for repair; parsed graph readings retain their revision comparison.

Parsed graph [`query`](docs/query.md) compares revisions, defaulting to fresh HEAD versus
saved workspace with spotlight-style --base/--target selection. Iterative ordered
last-occurrence walks print a selected-record overlay: current parents/text for
current nodes, former parents/text for nodes marked deleted. Valid revisions yield
an acyclic projection; invalid declared references retain missing endpoints and
finite cycle-safe readings. It is a reading, not a new canonical graph. Compact rails and full parent headers remain.
Default bodies occupy one line: single newlines become spaces and longer runs
become ` ¶ `. Types/change hints use lowercase words without a legend, and root
content has no extra indent. Parents use comma-space separators in every mode.
Default sources share one comma-separated line per node; --human keeps logical body
lines and lists each source separately. Both modes retain the same derived facts;
--human does not alter --json. Original bodies remain exact in JSON and node files.
Source hints respect strict/expanding/path-only permissions: accepted edits stay
quiet, while known contract transitions drive source-changed and original-graph ancestor effects.
Broken/uncertain links remain explicit. Raw source facts stay complete in JSON.
Known committed source blobs/anchors populate existing per-call caches in batches;
identical commits reuse a reader. No query cache survives the invocation.
Query builds change summaries; exact patches and literal review belong to `diff`.
Rooted subqueries accept an optional full node ID and --min-distance, --max-distance
or --influence. Inclusive integer cutoffs use <= for distances and >= for influence;
decimal percentages select exact ceil quotas from one reachable population. Full ID
ties are deterministic and multiple criteria combine by union. A shared graph batch
propagates distances forward and self-inclusive influence bitsets backward, releasing
masks after their last consumer. Scoped records keep full boundary parent references
and required old/new descendant source evidence; unrelated branches avoid resolver
work. Default unfiltered comparisons retain all records.
--with-ancestors completes the matched set with every selected-record ancestor after
quotas, preserving their original population and metrics. JSON separates matches,
added ancestors and omitted direct-child/sibling identities. Ancestor completion
uses one multi-source walk before the final view/source comparison. A root with
--max-distance 0 gives its complete upstream reading through this same query path.
The emitter formats once; advanced --max-bytes bounds its exact UTF-8 response,
envelope/control escaping and final newline, failing without partial success.
Canonical node schema and existing host operations retain their contracts.

## Local 0.1 distribution and onboarding

Python wheels/source distributions and a private three-workspace npm monorepo provide
separate CLI, VS Code and Electron products. One root lock and root commands install,
build/test and package offline UI assets/runtime and all bundled dependency notices.
The locally built VSIX installs into the owner's ordinary VS Code instance without
Marketplace submission; F5 remains a developer alternative. The portable desktop
uses an explicitly unpacked runtime allowlist and Windows ZIP/Linux tar archives;
Python/Git remain external. Artifact checks enforce versions, resources, runtime
membership and licenses and emit digests, never publication or owner installation.

New project initialization bundles a conceptual/process/CLI AGENTS.md and creates
it at the project root only when no entry occupies that name. Existing files,
directories and symlinks remain untouched. New instructions share the lock and
journal, exclusive publication and all-before-any recovery validation, while ordinary
mutations remain node-only. The guide is owner-editable text, not graph membership.

The introduction uses exact selected light/dark primary logos and explains intentions,
revisable conclusions, source realizations and owner delegation without semantic
proof or hosted-agent claims. Release guides distinguish actual Windows artifact
qualification from other targets and retain dependency-audit and authentication
compatibility limits. Parsed API-7 records retain logical bodies with CRLF normalized
to LF; raw documents, canonical files and diff are physical-layout evidence.

## Canonical files and grammar

Use a flat project-root `.specspec` with direct regular node Markdown files.
The unique manifesto contains integer `format_version: 7`. Requirements depend on
manifesto/requirement parents; implementation leaves depend on requirements. All
nodes form one rooted connected DAG. Frontmatter fields are `id`, `type`, `parents`,
manifesto `format_version`, optional implementation `sources` and optional namespaced
JSON-compatible `extensions`. Bodies carry binding current text and readable headings.

IDs are padded RFC 4648 Base64url over `secrets.token_bytes(5)`: **40 random bits**,
seven payload symbols plus `=`. Filename is `<id>.md`. Lock-scoped
creation retries exact/casefold collisions; input validation detects portable aliases.
Full identities and zero pad bits are canonical. VS Code associates `**/.specspec/???????=.md` and asks Python to validate
the actual resource. IDs and paths remain stable through body and parent changes.

Bootstrap the unique manifesto/version, then validate typed metadata, YAML keys,
alias/tag restrictions, file entries/paths, UTF-8 and the 1 MiB node-file budget.
Unsupported schemas/unknown fields produce diagnostics. Preserve body bytes and
unaffected frontmatter comments during targeted writes. Lists/headings structure a
coherent element; independently reusable/reviewable reasoning warrants another node.

The graph engine builds node/parent/child maps, deterministic heap-based Kahn order
and iterative closures/cycle witnesses. Node format 7 requires a transitively reduced
DAG: each direct parent adds ancestry. After basic graph checks pass, shared ancestor
traversals diagnose redundant edges with deterministic alternative paths. Validation
never normalizes edges. Managed candidates, native overlays, revisions and exact
staged blobs use this one authority. Rebuild per invocation; base checks are linear
with O(V log V) ordering cost, plus shortcut traversal/witness work. See
[graph structure](docs/graph-structure.md). Changes require reconsidering indirect
effects against both old and new graphs; implementation realization remains bounded.

## Transactions, deletion and native persistence

Managed operations diagnose saved and candidate graphs under a workspace lock,
allow graph-invalid intermediates and optionally require a valid complete result
with --require-valid. Safe identifiable target schemas and physical safeguards stay
enforced independently. They
stage same-filesystem bytes, journal originals/replacements outside `.specspec`,
byte-check targets, replace and validate again. Null replacement states mean physical
deletion. Interrupted writes block further mutations until recovery. Recovery accepts
known original/replacement/absence states and preserves intervening external text.
Its protection is bounded to cooperating writers/process interruption with explicit
filesystem-race and power-loss limitations.

Managed `delete` removes exactly selected node files, protecting the manifesto.
Surviving conclusions retain their body text and parent declarations, including
missing references, for deliberate reconsideration. Linked code remains unchanged.
Preview selected files, retained faults, potential downstream scope and final validity
with --dry-run. Assess only selected paths for untracked/ignored/staged/unstaged/
comment/rename/mode/conflict changes.
Unavailable Git assessment warns explicitly. Warnings precede unlinking; warned
noninteractive actions need `--yes`. Hosts confirm the backend scope/warnings and
submit a reviewed plan for direct locked rechecking. Success reports every removed ID.
Git predecessor trees retain reasoning; normal commit messages explain removal.

VS Code forms use non-writing Python overlays/plans and native WorkspaceEdit;
Save/autosave/undo/redo/dirty recovery belong to TextDocuments. Invalid text remains
repairable and native Save can persist it. Managed project actions require clean
SpecSpec documents. Missing-file buffers are validated then omitted from overlays;
absent-file edits fail. Electron/project saves use the managed writer. Per-view
unapplied-form recovery has separate explicit handling.

## Git snapshots, source regions and refresh

Read exact staged/commit blobs through NUL-delimited Git paths/object reads.
`check --staged` validates the intended index; owner-managed hooks/CI call it without
a SpecSpec installer. Optional `--sources` adds staged source resolution/retention. Compare full IDs, normalized records,
raw files and added/removed edges. Potential impact uses both
old/new closures and source references. Absent base graphs/genuinely unborn HEAD are
empty baselines; invalid/unavailable revisions receive diagnostics.

Default UI baseline is freshly resolved **HEAD**, including after staging. Display
removed base records as selectable read-only D ghosts until commit removes their
membership. Dirty orphan forms remain copyable/unsavable. Explicit comparisons have
independent per-view state. Shared Git watching observes relevant private/shared
metadata/ref directories, including detached/unborn/linked-worktree cases.

Sources use safe project-relative POSIX paths and optional descriptive symbols.
Whole-file hints are usable independently of Git. Anchored hints add full lowercase
SHA-1/SHA-256 blob, strict/expanding mode and sorted inclusive line ranges. Strict
reports internal edits; expanding absorbs contained changes; both exclude outer
insertions/gaps. Bounded/cached mapping reports ambiguity/deletion/unavailable or
unsafe data. Literal previews expose originals when target mapping is unreliable.
Git tree edges retain blobs. Explicit capture/reanchor follows normal native/managed
save ownership. Shared raw file impact remains conservative; query's compact cues
separately honor the reference's declared change permissions.

Watchers coalesce hints and retry transient reads, directly compare records and retain
native form/caret/cameras. Superseded generation/text reads have a distinct error;
bounded attempts coalesce a fresh automatic refresh without misdiagnosing invalid
files. Explicit working reads report retry and request a follow-up. Actual invalid
reloads show fresh diagnosable invalid graphs; unavailable transport/schema results
retain marked last-usable context. Same-node overwrites
require confirmation. Explicit Refresh and configurable
polling (default 0/off) remain. Watcher delivery depends on the filesystem.

Project-scoped bounded API channels reuse interpreter lifetime, with a separately
warmed read-only source channel. Each API-7 frame performs current validation and
file/ref/index reads. Ordinary CLI commands retain one-shot execution. Closing or
reconfiguring a project disposes its channels; failed mutations receive no automatic
replay. Preview replies match the published render and displayed commit. Native
bootstrap retries supersession before editor attachment. Both hosts share
asynchronous HEAD/ref watching; graph, Spotlight and canonical text notifications
coalesce independently of index stat-cache and Git-extension status churn.

## Shared visual graph

Use one local nonce-protected DOM/SVG renderer/template and shared guarded session.
Host ports provide selection/trust/dialogs/watchers/state/themes; project text is
literal. Bundle pinned Dagre/D3 and transitive license notices. Self-contained host
builds copy shared bytes. Electron uses sandboxed isolated preload, authorized main
IPC/asset handling and trusted launch-relative executable configuration. Python/Git
are external prerequisites. Agent transports are separately scoped follow-on work.

Focus the same native form within compact direct parents/children. Distinguish actual
parent links from candidates and derive unique all-depth downstream counts. Compute
minimum BFS/maximum topological path bounds per full revision. Target/base contexts
stay separate from comparison display unions and placement backbones.

Dagre places a deterministic deepest-parent backbone after all-parent earliest ranks;
every relationship renders. Intrinsic world sizes determine arrangement. Clip on
resize and navigate by a D3 camera with 12–250% pointer zoom, unconstrained pan,
a rounded floating zoom/framing HUD and native-gesture exclusions. Graph/node
framing uses icons; a contextual third/overview second framing icon arms rectangle
framing. Ctrl-drag (Windows/Linux) or Command-drag (Mac) captures the pointer and
inverts the starting camera. The rubber band stays latched after modifier release;
pointer release frames with 40px margins and up to 250% zoom. Graph/node framing
retains its 100% cap. Escape/blur/cancellation clears the tool, and four-pixel axis
thresholds retain the pose for tiny gestures. Native and highlight gestures keep
precedence. Current-scale text and independent overview/focus cameras retain editing.

Ordinary cards are 264×112 compact, 860 wide expanded. Implementation radius **0px**,
Requirement **24px**. Manifesto is 264×264 compact and expanded diameter
`ceil(hypot(822, intrinsicHeight)+48)` around the same native form. Actual shape ports
have 3-unit clearance, middle-40% circle attachments, bounding-box-clearing leads and
smooth tangent heads. Minimum paint floors are 1.6 screen-pixel strokes and 6-pixel
heads with compensated dashes. Camera changes update paint, not world arrangement.

The exact distance/type/revision spectrum is `#bc82c9`, `#7e97e6`, `#1facce`, `#37b390`, `#92a64b`,
`#ca8d3e`, `#dc7b7c`. Requirement index 4, Implementation 0, Added 3, M 1, D 6,
source-only 5. Distance `(d-1)%7`; neutral `#929baa`, distance/type root `#d3d3d3`.
Eight modes have concise color legends; revision colors the root by comparison too.
Influence counts self plus unique descendants, with a minimum of one. Absolute
influence uses `(c-1)/(M-1)` for the non-manifesto maximum M. Relative influence
scales cohort minimum to maximum, grouping by maximum manifesto distance. Their
logarithmic counterparts apply natural log before normalization: `log(c)/log(M)`
for absolute and `(log(c)-log(lo))/(log(hi)-log(lo))` for relative. All four modes use
continuous sRGB green `#4df884` → yellow `#e8d62c` → red `#ba2208`, with full
target/base context, shared lazy raw ranges, green tied cohorts and a neutral gray
manifesto. Git theme titles/corners and edge patterns
retain independent meaning.

Actual-size tints are 15% rest / 24% hover. As zoom decreases below 40%,
linearly blend those base fills to the painted border, reaching solid shapes at 16%.
High-contrast cards start from the theme canvas background. The white hovered
manifesto and strengthened colored borders are exact fill endpoints. Colored hovered borders/incident inks use
OKLCH L+.10 (cap .95), C×1.30, same H; neutral distance/type/influence root hover is white.
Darken outside immediate displayed hover context with card brightness(.45) and
35% ink / 65% black. Keep forms/caret/geometry stable and restore on exit.

Spotlight add takes full node IDs and one message, with optional --base/--target.
Explicit refs pin commits; the implicit default follows fresh HEAD versus workspace.
One immutable local-format-2 record stores the comparison, IDs and message in
Git-excluded `.specspec-local/annotations/`. Workspace targets also store capture
HEAD and a sparse map: SHA-256 checksums only for uncommitted added/modified nodes,
null for deletions. Clean Git nodes and committed comparisons carry no saved node
hashes. Git owns historical text; no raw-node archive or captured-text preview exists.

Selection switches comparison before applying identity-based highlights and framing
available target/deleted-base nodes in the full canvas. Workspace drift warns visibly
without suppressing useful rings. One --spotlight-color CSS variable starts white;
ring width max(5, 3 / k) follows graph scale with a 3px screen minimum and equal inset.
Shift-click toggles, Ctrl/Command+Shift removes, and Clear highlight clears the shared
manual/spotlight ID set. A message modal captures the current comparison and trusted
native overlays without saving documents or managed drafts. Spotlight show reports each
record's A/M/D/= statuses, missing/unavailable members and advisory warnings.

The dropdown, active identity and highlight IDs are per view. A round red badge
counts new records since opening, with zero initial/reload baselines; arrivals
preserve editing, camera and old entries. Independent watching includes historical
views. Explicit reviewed flush clears metadata and obsolete copies while keeping
editable IDs, specification and recovery data. Old local formats stay protected
until deliberate flush. [The spotlight guide](docs/spotlights.md) explains the data
structures, commands, warning limits and verification.

Ordinary curves and heads share darker neutral ink: 70% theme ink mixed with black
at 70% scale and above, decreasing linearly to 35% at 16% zoom. Diff/draft and
incident-hover inks stay distinct. Minimum screen dimensions, shape ports and world
layout retain their existing contracts. Tool-authored labels use concise positive
state/action copy. The canvas carries actual legends and floating controls; tutorials
and normalization explanations live in documentation. Project text and structured
validation evidence retain literal content.

## Examples, documentation and verification

Gantt is the sole maintained product example: independent current-schema graph,
complete portable eight-commit history, actual CLI receipts and stage ledger. Its
three agent-planned spec/code pairs include two major redirects. Every maintained
revision states that point's product positively; Git records changes. Existing manual
clones retain experiments. Every node-schema change reconstructs all maintained
example revisions/refs/receipts/source anchors and refreshes bundle/snapshot together.
SpecSpec's own development history retains its original commits. Small synthetic
graphs are focused test fixtures; the offline rainbow playground is a development tool.

The playground defaults to seven samples, L=.69/C=.12, hues 320→20. Added selects
nearest fixed hue 149.5°, then Requirement nearest unused 165° with reuse/earlier ties.
Copy JSON/CSS, retain valid preview on input errors and show gamut reductions. It
opens from local files independently of the graph runtime.

Keep an accessible offline engineering map with local links and current runtime
ownership; the graph remains binding. Preserve supplied art exactly and narrowly
scope generated local settings. Validate current graph/context/sources, exact staged
root/Gantt indexes, all maintained example refs, actual receipts and runnable models.
Run Python, shared UI and host-adapter suites plus scoped real-browser/host checks.
Shared real-host geometry uses reduced motion and unthrottled isolated hosts. The
shared UI allowance is 300s and native lifecycle 160s, with 400s Electron and 500s
VS Code aggregate guards. Individual operation
assertions/deadlines and production camera behavior retain their own contracts.
Evidence informs review within its dispatched platform/theme/fixture scope.

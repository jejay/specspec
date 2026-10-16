# Current technical conclusions

The binding specification is the intention-conclusion graph in
[`_specspec/`](_specspec/). [Its tour](docs/own-spec.md) distinguishes owner outcomes,
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

Use Python 3.11+, Hatchling, Click, ruamel.yaml and pytest. The importable domain
library and console/module CLI serve all hosts. Support pipx/uvx isolation and local/
Git installation; publication is separately authorized.

```text
src/specspec/
  model.py / format.py      # Current schema, diagnostics and targeted Markdown
  graph.py                 # Rooted DAG, deterministic order, iterative closures
  workspace.py             # Discovery, validated byte transactions and recovery
  deletion.py              # Descendant scope and uncommitted-file assessment
  git.py                   # Index/revision reads and semantic/source impact
  editor.py                # Non-writing native overlays and document plans
  source_schema.py         # Shared whole-file/region validation
  sources.py               # Bounded blob/range resolution and retention
  source_commands.py       # Inspect/capture/reanchor; deliberate source writes
  annotations.py           # Immutable local spotlights, retained bytes and resolution
  annotation_commands.py   # Public spotlight add/show/flush
  application.py / wire.py # Shared reads/plans and compact comparison projection
  output.py / cli.py       # Readable review presentation and API-6 envelopes
graph-ui-common/            # One DOM/SVG renderer, session, camera, build/template
vscode/                     # Document/project/view adapter and native facilities
electron/                   # Authorized main/preload/renderer and local storage
```

Adapters call the CLI with argument arrays, bounded UTF-8 stdin/output and a fixed
trusted executable. The Python library owns graph/schema/serialization rules.
API 6 structured stdout is one `{api_version, ok, result, diagnostics}` envelope; exit 0 means
success, 1 validation/rejected operation, 2 invocation/I/O failure. Diagnostics have
stable codes, severity, path/optional ID and actionable text. Body input supports files
or `-` stdin. Full-parent updates explicitly replace the supplied set.

The [compact command guide](docs/cli.md) defines eight everyday verbs with readable
text/Markdown defaults and explicit compact JSON. Full review diffs show all canonical
file hunks, semantic node/relationship changes and separate linked-source impact.
Comparison transport shares unchanged records; both hosts use the same read coordinator
with optional native overlays and working-first loading. Native persistence stays
separate from managed writes. Node format is **6** and protocol is **6**.

## Canonical files and grammar

Use a flat project-root `_specspec` with direct regular node Markdown files.
The unique manifesto contains integer `format_version: 6`. Requirements depend on
manifesto/requirement parents; implementation leaves depend on requirements. All
nodes form one rooted connected DAG. Frontmatter fields are `id`, `type`, `parents`,
manifesto `format_version`, optional implementation `sources` and optional namespaced
JSON-compatible `extensions`. Bodies are binding current text; summaries aid discovery.

IDs are padded RFC 4648 Base64url over `secrets.token_bytes(5)`: **40 random bits**,
seven payload symbols plus `=`. Filename is `<id><ascii-slug>.md`. Lock-scoped
creation retries exact/casefold collisions; input validation detects portable aliases.
Full identities and zero pad bits are canonical. VS Code associates `**/_specspec/???????=*.md` and asks Python to validate
the actual resource. Stable IDs survive body/parent/summary changes.

Bootstrap the unique manifesto/version, then validate typed metadata, YAML keys,
alias/tag restrictions, file entries/paths, UTF-8 and the 1 MiB node-file budget.
Unsupported schemas/unknown fields produce diagnostics. Preserve body bytes and
unaffected frontmatter comments during targeted writes. Lists/headings structure a
coherent element; independently reusable/reviewable reasoning warrants another node.

The graph engine builds node/parent/child maps, deterministic heap-based Kahn order
and iterative closures/cycle witnesses. Node format 6 requires a transitively reduced
DAG: each direct parent adds ancestry. After basic graph checks pass, shared ancestor
traversals diagnose redundant edges with deterministic alternative paths. Validation
never normalizes edges. Managed candidates, native overlays, revisions and exact
staged blobs use this one authority. Rebuild per invocation; base checks are linear
with O(V log V) ordering cost, plus shortcut traversal/witness work. See
[graph structure](docs/graph-structure.md). Changes require reconsidering indirect
effects against both old and new graphs; implementation realization remains bounded.

## Transactions, deletion and native persistence

Managed operations validate saved and candidate graphs under a workspace lock,
stage same-filesystem bytes, journal originals/replacements outside `_specspec`,
byte-check targets, replace and validate again. Null replacement states mean physical
deletion. Interrupted writes block further mutations until recovery. Recovery accepts
known original/replacement/absence states and preserves intervening external text.
Its protection is bounded to cooperating writers/process interruption with explicit
filesystem-race and power-loss limitations.

Managed `delete` unions requested nodes and **all** directed descendants, including
shared/partial children. Protect the manifesto and validate the remainder. Outside
parents and linked code files remain unchanged. Preview with `--dry-run`; assess every
affected path for untracked/ignored/staged/unstaged/comment/rename/mode/conflict changes.
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
raw files, filename-only changes and added/removed edges. Potential impact uses both
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
save ownership. Source impact remains conservative at file level.

Watchers coalesce hints and retry transient reads, directly compare records and retain
native form/caret/cameras. Same-node overwrites require confirmation. Invalid reloads
retain a marked last valid graph with diagnostics. Explicit Refresh and configurable
polling (default 0/off) remain. Watcher delivery depends on the filesystem.

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
frame/100% controls and native-gesture exclusions. Current-scale native text and
independent overview/focus cameras retain readable editing.

Ordinary cards are 264×112 compact, 860 wide expanded. Implementation radius **0px**,
Requirement **24px**. Manifesto is 264×264 compact and expanded diameter
`ceil(hypot(822, intrinsicHeight)+48)` around the same native form. Actual shape ports
have 3-unit clearance, middle-40% circle attachments, bounding-box-clearing leads and
smooth tangent heads. Minimum paint floors are 1.6 screen-pixel strokes and 6-pixel
heads with compensated dashes. Camera changes update paint, not world arrangement.

The exact spectrum is `#bc82c9`, `#7e97e6`, `#1facce`, `#37b390`, `#92a64b`,
`#ca8d3e`, `#dc7b7c`. Requirement index 4, Implementation 0, Added 3, M/R 1, D 6,
source-only 5. Distance `(d-1)%7`; neutral `#929baa`, distance/type root `#d3d3d3`.
Four modes have explanatory legends; revision colors the root by comparison too.
Git theme titles/corners and edge patterns retain independent meaning.

Shared tints are 15% rest / 24% hover. Colored hovered borders/incident inks use
OKLCH L+.10 (cap .95), C×1.30, same H; neutral distance/type root hover is white.
Darken outside immediate displayed hover context with card brightness(.45) and
35% ink / 65% black. Keep forms/caret/geometry stable and restore on exit.

Agent answers arrive through `spotlight add` with color names, full node IDs and
one message as direct arguments. Each color applies to following IDs; initial IDs
use purple. One immutable spotlight holds every colored set and its shared message.
Store it and retained node bytes in Git-excluded `.specspec-local/annotations/`
until explicit flush. The toolbar's Spotlights dropdown has one text entry per shot.
Selection paints all its exact-version colored 8px inset rings, closes the dropdown
and frames their union in the full canvas, retaining focused drafts. Compact version
counts replace detail/preview UI. Clear highlight removes rings explicitly.
A round red badge counts new shots since opening; initial entries count zero and
reload starts a fresh in-memory baseline. Arrivals preserve editing and camera.
The dropdown and version-aware editable highlights are per view; contents are shared
per checkout. Shift-click cycles red/blue/green/purple/turquoise/yellow/off and
Ctrl/Command+Shift clears one node. Manual and spotlight-applied rings share this
set; whole-set clear applies to both. The dropdown saves highlights with a message
as a new immutable spotlight, readable by an agent through spotlight show. Exact
retained/target/base/native-overlay bytes are captured without saving forms or
claiming a common commit; assembled records use highlights provenance. Flush
removes the store, leaving editable references independently clearable.
Watching is independent of graph refresh, including historical views. Internal
store/transport names remain independent of public naming. [The spotlight guide](docs/spotlights.md)
specifies arguments, version resolution, storage limits and verification.

Ordinary curves and heads share darker neutral ink: 70% theme ink mixed with black
at actual size and above, decreasing linearly to 35% at 12% zoom. Diff/draft and
incident-hover inks stay distinct. Minimum screen dimensions, shape ports and world
layout retain their existing contracts.

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
Shared real-host geometry uses reduced motion/unthrottled isolated Electron; VS Code
has 160s/160s phase guards and a tested 360s outer budget. Individual operation
assertions/deadlines and production camera behavior retain their own contracts.
Evidence informs review within its dispatched platform/theme/fixture scope.

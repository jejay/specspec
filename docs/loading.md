# Graph loading, derived caches and diagnostics

Both hosts first display a validated working graph with **HEAD comparison loading**
explicitly marked, then adopt the fresh HEAD/source comparison. VS Code native bootstrap
supplies that first snapshot when its actual document/generation stamp still matches.
Historical panels load their selected comparison directly. Provisional project
mutations/deletion/source capture stay disabled in the form; native input retains
its normal planner and save owner. Camera/focus/caret and drafts remain view-local.

A comparison failure becomes an explicit unavailable note on the current working
context. A current-file/overlay failure retains marked last-valid context and its
existing repair/mutation restrictions. Ready/render sequence and full-membership
acknowledgements still apply. This is useful context before comparison completion,
not permission to treat provisional Git information as complete.

## Backend work

Canonical Git snapshots read NUL-delimited literal tree/exact-index entries and
use bounded `cat-file --batch-check` and `--batch` calls. Object IDs are deduplicated
for I/O while each path retains its own entry diagnostics. Metadata batches contain
at most 256 objects; content chunks contain at most 8 MiB plus bounded framing.
Objects retain the 1 MiB node limit. Finite process/output budgets, exact identity/
type/size/content framing and locally available blobs protect the reader; no fetch,
checkout, staging, object/ref/index writes or automatic hooks occur in these reads.
Large graphs are chunked rather than truncated. Error/unsupported-schema/conflict
and unborn/absent graph semantics stay explicit.

The standalone `query` command also batches known committed source-file blobs and
region anchors into its existing invocation-local cache. Identical selected commits
reuse a code reader; workspace bytes remain fresh and separate from index entries.
There is no persistent or cross-call query cache. [Query profiling](investigations/query-performance.md)
records the source process-fanout bottleneck, fixed-input output equivalence and a
reproducible benchmark helper. These measurements exclude terminal rendering.

Round-trip YAML frontmatter is memoized by exact header text within the current
Python process, with isolated mutable copies, at most 256 entries and an 8 MiB
header-text budget. Body text, node schema, graph, source paths and runtime recovery/
lock checks remain current. This avoids repeated parsing of unchanged headers
within overlays, worktree/base reads and library use.

The shared project read coordinator serves Electron and VS Code. Electron supplies
saved files; VS Code adds native overlays. It shares identical **in-flight** reads using
actual open-document contents, versions, dirty/EOL state, generation and base/target. Each view
receives an isolated payload. Later/explicit refreshes do fresh reads, even if no
watch notification arrived. Failed/changed/closed reads are not adopted as current.
`SupersededReadError` distinguishes generation/text races from invalid files and
closed projects. Each refresh makes bounded attempts; exhausted automatic attempts
coalesce a fresh event-driven refresh while retaining presentation/action state.
Explicit working reads report retry and schedule a follow-up. Actual invalid reads
still enter the marked last-valid repair state. Disposal cancels pending work;
this retry path introduces neither recurring polling nor longer operation deadlines.

An optional API-6 application `read` with `cache: true` returns bounded `base_cache` byte hints, held
only in project memory and removed before sending display data to the renderer.
They contain a resolved commit and at most 2 MiB of canonical Git file text. A later
read may send those hints; Python freshly resolves the ref and lists current entries,
batch-checks object availability/type/size, and verifies hinted bytes against each
Git blob address before reuse. Mismatches are reread locally; missing blobs remain
unavailable. HEAD movement changes applicability; staging never substitutes index
membership for HEAD. The internal Snapshot commit is not canonical node metadata.
Git content addressing for a reader cache does not introduce node edit fingerprints,
`--expect`, approval gates or persisted cache files.

Managed actions reread/validate authoritative files under their existing writer
lock, replan reviewed deletion scope/warnings and compare original bytes. Exact-index
checks still assess exact staged objects. Caches do not authorize mutations. Polling
remains default-off; notifications are hints, with explicit Refresh available.

API 6 transports a single target snapshot plus previous records only for changed/
deleted nodes. The shared adapter reconstructs complete revision structures for the
renderer; normal refreshes no longer run export followed by diff. Historical reads
bypass workspace buffers. Native plans and managed writes retain separate owners.
See [command/protocol details](cli.md).

## Project-scoped API channels

The hosts reuse two bounded Python processes per project/executable configuration:
one for application requests and one for read-only source previews. Both warm on
the first authorized API call. `api --stream` accepts newline-delimited API-6 JSON
and returns one ordinary envelope per frame. The one-shot CLI remains available.
Each frame still validates current files, locks/journals, native text and Git state.
Only interpreter lifetime and bounded derived caches persist between requests.

Channels serialize their frames and bound input/output, pending requests and elapsed
time. Close/switch/configuration changes dispose them. Transport failure rejects
pending work; a later request can open a fresh channel, while mutations are never
automatically replayed. A dispatched mutation with no confirmed response reports
its uncertain outcome for inspection. The preview lane checks published render and
displayed commit identity, so queued background work cannot retarget a clicked source.

HEAD/ref watching is asynchronous and shared by both hosts. Canonical text and
Spotlight metadata have independent watchers. Polling zero stops periodic ticks,
while watcher hints, explicit Refresh and already-requested coalesced work remain
valid. Initial Git discovery can therefore legitimately refresh after polling is
disabled. [Polling lifecycle tests](investigations/polling-test-race.md) control those
independent events and await disposal rather than assuming a wall-clock quiet window. Index stat-cache writes and Git
extension status churn leave HEAD-to-working presentation unchanged. Explicit
staged source actions read the current index when invoked.

## Loading diagnostics

Enable this resource-scoped setting when measuring a project:

```json
{ "specspec.traceLoading": true }
```

The SpecSpec output channel records discovery/watch setup, CLI durations, readiness,
first-working-render, full-comparison-render and client render acknowledgement
measurements. Phase records contain durations and counts, not body text/credentials.
Host phases use host clocks and renderer durations use the client clock; compare
elapsed durations, not absolute timestamps across remote machines. Normal executable
/error diagnostics remain available separately. Disable the option after measurement.

Measure cold/warm opens, project/native tabs, multiple tabs, representative graphs
and actual remote clients. Backend timing is not full visible load time. CPU, filesystem,
process-start, transport, asset and layout costs vary. Existing individual deadlines,
production geometry/camera and semantic checks were not relaxed to make loading look
fast. No subsecond or universal delivery/performance guarantee is inferred from tests.

The [loading investigation](investigations/vscode-loading.md) preserves the original
measurements, failed probes and narrow batching experiment. Its baseline numbers are
historical evidence, not current release benchmarks. Remote setup and qualification
are described in [remote workspaces](remote-workspaces.md).

[Installed-host verification](investigations/host-smoke.md) describes the complete
Electron/VS Code suites, aggregate phase guards and causal transport/read regressions. Test guards are separate from the
unchanged individual and production operation deadlines.

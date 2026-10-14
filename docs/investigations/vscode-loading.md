# Investigation: slow VS Code graph loading

## Question, scope and status

The owner reports that the VS Code graph takes ages to load while pan/zoom and
other camera interaction feel fine. They ask whether a Rust server or new caching/
intermediate data structures would help. This investigation profiles the backend
loading path, tests a disposable optimization and records prioritized conclusions.
It changes no product runtime, binding graph, schema, deadlines or renderer.

Baseline: `829a306`. The working root has **121 nodes**, including four concurrent
architecture nodes outside the preceding cleanup commit; committed HEAD has **117**.
The maintained Gantt clone has **22** current and HEAD nodes. This report is
investigation/evidence, not a binding performance contract or completed optimization.

## Conclusion

**Batch Git object reads first. Do not start with a Rust rewrite.** The current
`git_snapshot()` launches two Git processes per canonical file, and a HEAD-relative
load repeats that work on every request. There is direct evidence that this dominates
loading in the measured Windows environment.

A task-local batching prototype preserved the entire `editor` result for both
normal valid fixtures. Through the existing shared Node bridge it reduced the
root backend call from a single **34.89 s** baseline observation to a three-sample
**3.23 s** candidate median; Gantt went from **8.49 s** to **2.85 s**. Different
sampling and scheduling prevent treating those ratios as a benchmark guarantee.
The result nevertheless makes batching a much better first implementation candidate
than a language port, new graph structure or persistent server.

## What actually loads

There is currently **no continuously running Python server**. The adapter starts a
fresh Python CLI process for requests. Camera work runs in the client webview and
therefore can remain smooth while a backend read is slow.

### Project panel

1. Discover the nearest project; establish canonical/Git watchers.
2. Create the webview and wait for its `ready` message.
3. `GraphSession.refresh()` → `ProjectDocuments.readGraph('HEAD')`.
4. Spawn `specspec editor --base HEAD --json`, with open-document overlays.
5. Read worktree node bytes, parse YAML/schema and build the valid graph.
6. Read/parse HEAD's graph, derive semantic diff and file-level source impact.
7. Encode/decode JSON and post the snapshot/diff to the webview.
8. Create/measure cards, run layout/routes and receive the render acknowledgement.

### Native node-file editor

`resolveCustomTextEditor()` first calls `project.documents.request()` with **no
base**, to identify the bound node. After custom-editor wiring and `ready`,
`view.open()` reads the graph again **with HEAD**. Thus the first useful normal
native load currently needs two Python requests and two working-graph reads, plus
one HEAD read. The earlier snapshot is not used for the initial rendered graph.

Both flows include discovery/watch setup, asset delivery, handshake and browser
layout outside the CLI timings below. The report did not measure those full UI
phases. Duplicate bootstrap reads, window startup and rendering may also contribute;
the measured Git bottleneck is not claimed to be the exclusive cause of every delay.

### Concrete amplification in Git reads

`src/specspec/git.py:git_snapshot()` lists index/tree entries, then for each
eligible file invokes:

```text
git cat-file -s <object-id>
git cat-file blob <object-id>
```

For HEAD's 117 node files that is **234 object subprocesses**, plus repository/ref/
listing/impact calls. For Gantt it is **44** object subprocesses. Snapshot/schema
parsing still happens afterwards. These are node-graph object reads, not source-region
resolution: `SourceReader.batch()` already batches source anchor objects, but
`git_snapshot()` does not use a corresponding batch path.

Independent views also perform their own reads after project notifications.
`ProjectDocuments.readGraph()` has before/after generation/document checks, but no
project-wide shared in-flight read or snapshot cache. Optional polling stays off;
adding polling would increase this work, not make the initial request faster.

## Measurements

Environment: Windows 11, Python **3.14.5**, Git **2.52.0.windows.1**, Node **24.21.0**.
Sequential local measurements with ordinary warm filesystem caches, no artificial
cold-cache reset. The root's canonical files total **113,001 bytes**. The Gantt
clone totals **12,726 bytes**. No real SSH/tunnel session was involved.

Git optional locks and lazy fetch were disabled for the investigation. Requests
were read-only; no node/source writes, index staging, commits, hooks or resets.
Each result's API success/schema envelope was checked.

### Python subprocess, three samples per operation

| Operation | Root median | Gantt median |
| --- | ---: | ---: |
| `--help` (process plus CLI imports/help, not pure interpreter startup) | 1.07 s | 1.08 s |
| `export --format json` | 1.87 s | 1.80 s |
| `editor --json`, empty overlays, no baseline | 1.84 s | 1.81 s |
| `editor --base HEAD --json`, empty overlays | **54.67 s** | **12.99 s** |
| Existing two-request native backend path, sum of medians | 56.51 s | 14.80 s |

The last row is an arithmetic backend estimate, not an observed native editor load.
Root HEAD-relative output was approximately **567 KB**; no-baseline output was
approximately **185 KB**. The result carries the current snapshot and diff's
base/target records, so target data is duplicated in the serialized response.
Pretty JSON and duplication may matter over slow links but do not explain the
large measured local difference by themselves.

### Profile details and important discrepancy

An in-process library request in the top-level probe took **5.45 s**, substantially
less than the piped CLI subprocess. Its phase timings were approximately:

- Worktree file reads: 0.016 s; runtime-state checks: 0.010 s.
- YAML reads for worktree plus HEAD: 0.424 s inclusive.
- Schema normalization: 0.023 s; two graph builds: **0.0011 s** combined.
- HEAD snapshot: **4.99 s**, including 234 individual object process calls.
- Semantic diff: 0.008 s; source-change impact: 0.130 s.

Those phases overlap and must not be summed. Instrumentation/profile overhead and
execution context also differ from the production request.

A cProfile probe *inside a subprocess with piped input/output* took **61.71 s**.
Of 245 subprocess calls, **55.23 s** accumulated in Windows `CreateProcess`, while
this Python process used around **2 s** CPU. Object-size reads accounted for
29.06 s and blob reads for 28.52 s. This supports the process-amplification diagnosis
rather than a CPU-heavy graph algorithm. It does not establish why Windows process
creation is so costly in this context.

Using `/dev/null`-equivalent Git stdin or giving the Python child a file instead
of piped stdin still took about **54.6–54.8 s** inside the child. A separate
`CREATE_NO_WINDOW` experiment exceeded **120 s** and was stopped; it was not adopted.
Do not turn these observations into an unproved antivirus/console diagnosis or a
recommendation to disable security software.

### Existing Node bridge versus disposable batching candidate

The actual shared `invoke()` bridge was used, with its existing API 5 parsing,
shell-free execution, input/output bounds and timeouts. This still excludes VS Code
webview, discovery and rendering time.

| Fixture | Existing bridge, one sample | Batched bridge, three samples | Candidate median |
| --- | ---: | --- | ---: |
| Root | 34.89 s | 2.80 / 4.27 / 3.23 s | **3.23 s** |
| Gantt | 8.49 s | 2.85 / 3.03 / 2.79 s | **2.85 s** |

The direct Python candidate also returned complete results identical to the
unmodified library for both fixtures in three runs each. Its medians were 4.97 s
and 4.36 s. Context/scheduling variation is material: compare like-for-like paths,
retain all samples and do not promise a universal speedup or subsecond load.

The candidate replaces the per-file size/content subprocesses with one
`cat-file --batch-check` and one `cat-file --batch` request. It reads exact sizes,
checks blob identity/type and compares complete backend results. It is a **normal-
case proof of concept**, not production code: it does not cover staged conflicts,
absent/unborn baselines, malformed entries, partial reads, comprehensive resource
limits or all error paths. Nothing was patched in the product checkout.

## Prioritized improvement plan

### 1. Batch canonical Git object reads

Extend the existing authoritative snapshot reader, using bounded metadata and
content batches. Deduplicate object IDs; preserve one path record per tree/index
entry. Inspect sizes/types before requesting bodies; enforce individual and aggregate
budgets and handle exact binary framing/short reads/errors. Keep proper diagnostics
for modes, symlinks, nested/unsafe paths, staged conflicts, missing objects and
unsupported current schemas. Preserve SHA-1/SHA-256 repositories and empty/unborn
semantics. Reuse source-reader ideas where appropriate, not its source-specific
line/UTF-8 limits as a replacement node schema.

This keeps Python and the current CLI ownership. It targets the demonstrated
bottleneck without a cache invalidation or worker lifecycle redesign.

### 2. Remove duplicate initial reads; share in-flight project reads

Have native editor bootstrap and first render use a single trustworthy result
where possible. Reuse only if document versions/text/generation still match;
custom-editor wiring must remain asynchronous to avoid the documented lifecycle
deadlock. Never attach the latest document version to an older snapshot.

Coalesce identical concurrent reads across views of the same project/base/document
state. Cache results at project scope while each view retains its own focus/cameras/
comparisons and recovered input. Invalid overlays and queued writes remain visible;
read sharing must not defeat the existing version/text checks or dirty-document guard.

### 3. Cache the expensive immutable baseline, then unchanged parsed nodes

Use the existing `Snapshot` and `Graph` structures. The graph already stores node,
parent and child indexes; rebuilding adjacency is not the measured problem.

- Resolve HEAD/ref freshly, then reuse a bounded immutable snapshot keyed by the
  resolved commit and project subtree/repository identity. HEAD movement changes
  the key; staging does not replace the HEAD baseline.
- For worktree reads, consider transient parse reuse based on exact file bytes,
  path and current parser/schema version. Body-only edits and repeated open-buffer
  overlays need not reparse every unchanged frontmatter.
- Recheck relevant source-path existence and runtime lock/journal state; those are
  not necessarily properties of immutable node bytes.
- Watcher events are hints, not complete change logs. Do not trust only mtimes or
  missed notifications for correctness. Bound memory and evict/dispose/reload safely.
- Managed mutations still take the writer lock, reread authoritative files, replan
  deletion scope/warnings and compare original bytes. A display cache is not mutation
  consent or a substitute for exact-index validation.

Commit/blob addresses here identify Git data; no new persisted node fingerprints,
`--expect` gates, approvals or schema fields are needed. Keep cached data derived,
revisable and outside the canonical specification.

### 4. Improve perceived loading and measure the complete UI path

After the inexpensive working graph is valid, consider displaying it with an
explicit **comparison loading** indicator rather than a blank graph while HEAD and
source impact finish. Add the verified comparison as a later phase without calling
it unavailable/complete prematurely. Guard stale replies, input/caret/camera and
read-only historical/ghost semantics. This is a UX choice that needs separate
specification and tests, not permission to omit validation or hide Git uncertainty.

Instrument timestamps for discovery/watch setup, Python launch, worktree/HEAD reads,
JSON transfer, `ready`, first useful graph, layout/routes and `rendered` acknowledgement.
Measure cold/warm loads, project/native tabs, multiple tabs, actual installed VS Code,
larger graphs and later SSH/tunnel clients. Keep production operation deadlines and
geometry assertions; extending test timers does not improve loading.

### 5. Only then consider a persistent Python worker

A per-project worker can amortize CLI imports and own bounded parsed/immutable
caches. CLI users and the worker should call the same domain library. Managed writes
retain current lock/journal/recovery and native Save stays with VS Code.

The benefit must justify framing/request IDs, cancellation, output limits, stderr,
trusted executable/version negotiation, crashes/restarts/disposal, external edits,
concurrent clients, and remote disconnect/unknown-operation outcomes. A worker must
not automatically retry destructive commands after losing a reply. Start with
measurement after batching: it is much less complex to remove hundreds of Git
processes than introduce a new service lifecycle immediately.

## Rust assessment

Rust is a possible later implementation choice, not the first remedy supported
by these measurements. Rewriting orchestration while still spawning two Git
processes per node leaves the principal amplification intact. A Rust reader that
uses direct Git libraries could avoid that work, but Python batching has already
shown that a language port is not required to achieve the large first reduction.

A port becomes more credible if profiles after batching/read sharing show dominant
CPU or memory cost at the desired scale, or there is a separate delivery goal for a
single native binary. It would need to preserve exact schema/ID behavior, strict
YAML restrictions and round-trip comments/quotes, native document plans, recovery,
Git semantics, source-region uncertainty, diagnostics/API and cross-platform behavior.
Do not infer those equivalences from faster code or passing ordinary fixture tests.

## Evidence and next action

All probe code, original samples and profiles are retained under
`.specspec-local/vscode-loading-investigation/`:

- `measure.py`, `measure.log`, `measurements.json`, `editor-head.pstats`;
- `child-profile.py`, `stdio-probes.json`, `pipe*.pstats`, `file.pstats`;
- `failed-window-probe.txt`;
- `batched-probe.py`, `batched-probes.json`;
- `node-bridge.json`, `node-batched.json`.

These are read-only task-local experiments, not shipped alternate readers. Actual
results and the failed experiment are retained. No permanent compatibility reader,
Git metadata changes or example-history rewriting was introduced.

Recommended first implementation: bounded batched node-object reads with complete
snapshot/error/temporal/source/index regressions, then eliminate duplicate bootstrap
and project reads. Re-measure full UI loading before committing to a daemon or Rust.
A future authorized implementation should update its binding choices separately and
verify exact staged root/Gantt source indexes; this investigation has not entered
that implementation phase.

Related: [remote-development investigation](vscode-remote-development.md),
[native persistence semantics](../native-editors.md),
[current specification tour](../own-spec.md).

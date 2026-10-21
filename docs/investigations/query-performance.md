# Query: invocation-local source-read batching

## Measurement scope

Measured on Windows 11 / CPython 3.14.5 in the development environment. Each CLI
trial starts a fresh Python process and captures stdout; OS/filesystem caches are
not flushed. Three runs per output format are observations, not latency guarantees.
Separate cProfile probes time read/render/JSON work and count Git processes.
They include instrumentation overhead and do not measure terminal rendering.

The original live checkout had 180 nodes, 542 source rows and roughly 160 distinct
committed source blobs. Plain CLI runs took 11.23–25.03 s (median 24.45 s); JSON
runs took 11.22–24.87 s (median 21.66 s). The instrumented read took 9.15 s, versus
15 ms rendering and 6 ms JSON serialization. Source reads launched **324 cat-file
processes**: a metadata/content pair per first blob read. Eight rev-parse calls
consumed about 0.25 s, so resolving refs was not the dominant cost.

A later non-overlapping post-change run of the live checkout measured plain CLI
2.86–3.85 s (median **3.07 s**) and JSON 2.96–3.89 s (median **3.73 s**), with four
source cat-file processes. The self-specification had grown to 181 nodes/546 rows as
this work updated its own docs and implementation links. Treat that roughly 8×/5.8×
median reduction as a local observation; the fixed-input comparison below controls
for self-referential file changes and establishes exact output equivalence.

## Change

Populate the existing `SourceReader.blobs` cache in bulk with known regular-file
blob addresses from the selected committed tree, alongside stored region anchors.
Previously only anchors were prefetched; ordinary whole-file paths each triggered
two Git processes on their first read. Keep duplicate source rows while deduplicating
object I/O. Identical selected commits reuse one code-version reader.

This is **within one invocation only**. There is no disk cache, cross-call result
cache, watcher dependency or saved mtime assumption. New calls resolve refs and
read saved files freshly. Workspace contents never come from index blob entries.
The existing path, entry, object, line, mapping, rename and byte limits remain in
force. Oversized objects remain unavailable without reserving unread content bytes
and thereby starving unrelated eligible objects in the same batch.

## Fixed-input comparison

An independent current-schema Git workspace keeps 180 nodes, 542 reference rows and
170 source paths fixed across before/after measurements. It includes whole-file and
strict/expanding references, permitted edits and a missing path. It is external to
this checkout, with its own local Git history. No maintained bundle or manual clone
was rewritten for this measurement.

| Measurement | Before | After |
| --- | --- | --- |
| Plain CLI median, 3 fresh processes | 18.65 s | 3.46 s |
| JSON CLI median, 3 fresh processes | 12.44 s | 3.57 s |
| Instrumented read | 11.11 s | 2.13 s |
| Source cat-file processes | 340 | 4 |
| Plain output | 39,548 bytes | identical SHA-256 |
| JSON output | 348,318 bytes | identical SHA-256 |

All three output digests per format agree before/after. The plain median improved
about 5.4× and JSON about 3.5× in these samples. Instrumentation counts in this table
cover source `subprocess.run` reads; canonical graph object reads already used the
separate bounded Popen batch reader. The maintained benchmark helper counts both.

The post-change profile shifts most remaining read time to current graph/YAML
validation; source comparisons fell from roughly 9 s to 0.56 s in the fixed fixture.
Python startup, fresh Git metadata and filesystem reads also remain. This change
does not bypass validation, silence uncertainty or promise subsecond delivery.

## Repeat and protect

```sh
python tools/benchmark_query.py --root . --runs 3 \
  --output .specspec-local/query-performance/after.json
```

The helper writes a JSON report, `.prof` and `.profile.txt` next to the chosen output.
Use an unchanged external current-schema workspace for strict before/after output
comparison; this repository's self-references naturally change when its own code or
specification is edited. For maintained temporal tests use the independent Gantt
bundle, not obsolete root specification revisions.

Regression tests compare batched/lazy facts on fixed fixtures, count Git calls
rather than asserting wall-clock deadlines, cover identical commits, ensure dirty
workspace bytes do not become index bytes, preserve per-call freshness and budgets,
and exercise missing/oversized objects alongside eligible sources. Shared source
inspection and contract-aware query hints retain their established meanings.

The query optimization passed Python/shared/adapter/Electron suites, Ruff,
working/exact-index source checks and the eight-revision Gantt verifier. The
[polling investigation](polling-test-race.md) causally reproduces the intermittent
VS Code assertion as a late watcher refresh counted as a poll, and replaces the
quiet-window assumption with controlled clocks/discovery. Product scheduling and
operation deadlines remain unchanged.

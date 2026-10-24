---
id: Kxh7M4Q=
type: implementation
parents:
- B6y6hgo=
- z9YKFeE=
- -fXS-dI=
sources:
- path: src/specspec/query.py
- path: src/specspec/cli.py
- path: src/specspec/output.py
- path: tests/test_query.py
- path: tests/test_cli_compact.py
- path: tests/test_repository_spec.py
- path: docs/query.md
- path: docs/cli.md
- path: example/gantt/history/verify.py
- path: src/specspec/query_sources.py
- path: tests/test_query_sources.py
- path: src/specspec/sources.py
- path: tests/test_sources.py
- path: tools/benchmark_query.py
- path: docs/investigations/query-performance.md
- path: src/specspec/query_select.py
- path: tests/test_query_select.py
- path: tests/test_query_ancestors.py
  symbol: ancestor completion, neighbor oracles and exact budgets
---
# Render complete selected-record query reads with contract-aware source hints

query.py reuses spotlight snapshot selection and semantic comparison, diagnosing
both selected revisions. A non-writing display projection chooses target records
for current nodes and base records for deleted nodes, each with that record's own
parents. Iterative reverse/forward walks render one overlay with full sorted parent
headers, compact rails, last-occurrence ownership and complete default one-line body readings. The
projection preserves chosen edges without canonical reduction or type/root checks;
for valid revisions its construction
is acyclic even when a full edge union would be cyclic. Invalid projections use
finite cycle-safe component roots and explicit missing endpoints.

Lowercase added/modified/deleted identify node changes. File-only marks
literal-only changes. Source-changed identifies known contract changes and
ancestors in both original graphs, independently of
shared conservative file-impact facts. Normal records and permitted code edits
stay unmarked. Query keeps summaries and reconstructed original graphs; diff owns
canonical patch review and raw LF-exact textual changes.

query_sources.py retains exact declaration multisets and cached shared readers.
Known committed source blobs and anchors populate the existing per-invocation cache
in batches; identical selected commits share a code reader. Workspace contents stay
fresh and independent of the index. Shared batch admission charges accepted bytes,
keeping oversized-object failures separate from eligible blobs. Process-count and
fixed-input equivalence tests protect this optimization; tools/benchmark_query.py
records fresh-process timings, cProfile stages and Git process counts. The performance
investigation records measured scope and remaining subprocess/YAML costs.
Bytes, trusted logical text and coordinates remain separate raw JSON facts. A
contract comparison uses strict/expanding/path-only semantics: reliable permitted
relocation/outside edits, expanding internal edits and whole-file content edits
stay quiet. Missing/strict-conflicting links and their restoration are known
contract transitions; ambiguous/unavailable evidence stays uncertain. Binary or
budget-limited whole-file contents do not invalidate an existing path-only link.
One-line readable rows show the selected location, reference +/- and relevant
broken/uncertain/restored hints. Complete metadata and diagnostics remain in JSON.

Tests combine independent literal unfolding and selected-parent overlay oracles,
reparenting/full-union cycles, ghosts with shared parents, changed node types,
introduced shortcuts, distinct roots, deep/exponentially shared graphs and all
retained Gantt revisions. Contract matrices cover permitted versus breaking edits,
strict conflicts, expanding changes, moves/renames/gaps/boundaries, restored and
pre-existing broken links, unavailable anchors, binary/large whole-file hints,
caching, original-graph ancestor ripple, declaration independence and historical
selection. Plain text/metadata, source facts, exact diff application, saved-buffer
semantics, read-only Git/files and legacy pipe safety retain regression coverage.

body_line normalizes CRLF and replaces single LF runs with a space and longer runs
with " ¶ ", without truncating text or changing original bodies. The readable
renderer spells out types and change hints, carries revisions/notes without a legend,
and aligns root content at column zero. Golden and newline-run matrices cover
paragraphs, headless text, Markdown markers, other whitespace, controls and deleted
bodies. Complete original bodies remain reconstructible in JSON and diff. The
one-line projection is the ordinary reading behavior; --human retains logical body lines.

query_lines/render_query accept a presentation-only human option; the CLI forwards
--human for text while --json retains its identical complete comparison. Every
parent header uses comma-space separators. source_item retains one reference's
location and hints; compact metadata joins all items under one sources prefix,
while human metadata uses source_line once per occurrence. Empty lists add no row,
and duplicate occurrences stay visible in either format. Rendering does not change
snapshot selection, source reads, contract classification or cache lifetimes.

Regressions cover compact/human golden reads, source aggregation and duplicates,
comma-bearing paths and disjoint ranges, uncertain/removed/deleted source items,
parent sorting in both modes, original multiline whitespace and control safety,
identical JSON, read-only Git state and maintained temporal graph traversals.


query_select.py computes one rooted population and shared metric batch, selecting
inclusive absolute sets or exact rational ceil-percentage quotas in metric/ID order.
Integer descendant bitsets count influence once per node with last-consumer release;
minimum/maximum distances share a forward pass. Independent frontier/path/closure
oracles cover the ranking equivalence and selection union. read_query builds the
projection once before source reads and reuses its induced view for either renderer.
Scoped comparison records retain external parent IDs and all necessary source facts.
query_sources filters declaration owners to the old/new descendant evidence scope
and propagates known changes with multi-source ancestor walks, preserving selected
badges when the breaking declaration itself lies outside the selected binding set.
Tests cover scoped reconstruction, selection provenance, deleted roots and shifted
relationships, outside evidence, empty/unrelated source avoidance and read counts.


Ancestor completion retains matched IDs and their metric provenance, then walks
all selected-record parent paths once and adds the deduplicated ancestor bindings.
The same induced view feeds compact/human output, reconstruction and source scope.
Surrounding IDs come only from omitted children/siblings of the original matches;
shared matched parents contribute their child sets once. Empty selections remain
empty, and complete unfiltered comparisons need no extra projection. The query
preamble distinguishes match quotas from extra ancestors, which may lie outside
the rooted population. CLI query carries --with-ancestors and an advanced exact
UTF-8 byte budget through a single-format emitter; there is one ancestor-reading
command. Tests cover independent closure/neighbor oracles, multi-parent completion,
ancestor provenance, historical ghosts and changed parents, representation/budget
boundaries, complete source evidence and invocation-local pass/read counts.

# Read current specifications with change hints

```sh
specspec query                                      # Fresh HEAD → saved workspace
specspec query --human                              # Multiline bodies, individual sources
specspec query --max-distance 2                     # Root plus longest-path levels 1 and 2
specspec query --max-distance 50%                   # Half the reachable graph, rounded up
specspec query qowy5AI= --influence 5                # Custom root; self-inclusive influence >= 5
specspec query --min-distance 25% --influence 25%    # Union of independent selections
specspec query 6EmKDz8= --max-distance 0 --with-ancestors # One node's full justification
specspec query qowy5AI= --max-distance 2 --with-ancestors # Slice plus every ancestor
specspec query --base release --target workspace
specspec query --base main~2 --target main
specspec query --json
```

A parsed graph `query` is a revision comparison, like [spotlights](spotlights.md), but its
readable output focuses on **current state**, not patch text. Each surviving node
shows all target body content once, projected onto one line. Deleted nodes appear
among the others, under their former parents, with `[deleted]` and their base content.
Old wording for modified nodes and exact text hunks belong to `specspec diff`.

```text
├─implementation AAAAAAQ=save-edits @ AAAAAAI=, AAAAAAM= [source-changed]
│ sources: src/save.py [conflict], src/store.py:2-8
│
│ Save each edit automatically. ¶ Keep the current document visible.
└─requirement AAAAAAU=removed-rule @ AAAAAAI= [deleted]
  The deleted binding's old text.
```

## Rooted subgraph selection

With no selection arguments, query reads the complete comparison. Supply an optional
full case-sensitive `NODE_ID` to start at a current or deleted record; otherwise
metric queries start at the target manifesto. A root by itself selects all its
reachable records. The population includes that root and each unique descendant
in the selected-record graph: target parents for current nodes, former parents for
deleted nodes. Different former manifesto roots remain in an unfiltered reading;
select a former root explicitly to search its separate deleted component.

| Option | Priority | Inclusive absolute cutoff |
| --- | --- | --- |
| `--min-distance N` | Smallest shortest path first | Shortest directed path from query root **<= N** |
| `--max-distance N` | Smallest longest path first | Longest directed path from query root **<= N** |
| `--influence N` | Highest influence first | Self plus unique descendants **>= N** |

Distances count edges, with zero at the query root. Influence has a minimum of one
and counts shared descendants only once; it is absolute, not normalized or logged.
Compute these values on the full rooted population, before applying any criterion.
For example, `--max-distance 2` includes the root and nodes whose longest path is at
most two edges. A shared node reached by a short and a longer path uses the longer
one for maximum distance and the shorter one for minimum distance.

Each option also accepts a decimal percentage in `[0,100]`. Select
`ceil(population * percentage / 100)` records in that metric's priority order,
breaking ties by ascending full case-sensitive ID. Thus `50%` selects 62 of 124
nodes, including the root; `0%` selects none, and `100%` selects the population.
Rounding uses exact decimal arithmetic. Absolute cutoffs are nonnegative integers.

Multiple criteria select **independently against the same population**, then query
returns their **union**. Their limits do not constrain one another or shrink the
next criterion's denominator. The output retains ID-ordered last-occurrence layout,
not search-priority print order. No extra ancestors or bodies are inserted to fill
missing parent links by default; every selected record still states all its parent
IDs. `--with-ancestors` explicitly completes their upstream bindings after selection.
`--human`, version selection and JSON work with the same selected set.

JSON `selection` identifies `root`, `population`, union `ids`, induced `edges`,
`boundary_parents` and `partial`. Each `queries` entry records its metric, limit and
priority-ordered `nodes` with IDs and values. Base/target/before bindings, node/file
changes and affected sets are scoped to those IDs. Full parent references and their
edge deltas remain, including boundary parents outside the view. Reconstruction
recovers the selected part of each original revision; snapshot `valid` describes
the original validated graph, not a claim that a partial view is canonical.

Source badges retain their original-graph meaning: an excluded descendant's broken
link can affect a selected ancestor. `source_evidence_ids` and complete
`source_resolutions` retain that necessary evidence even when its owner has no
visible binding. Unrelated branches need no source resolution. Zero-percent-only
criteria skip metric work; any empty selection skips code reads. Both saved graphs
are still validated.

## Complete the justification of a selection

`--with-ancestors` has one meaning: **add every ancestor of every matched node**.
It runs after the ordinary selection and independent metric unions. Metrics,
priority order, rooted population and percentage quotas retain their original
meaning; additional ancestors consume no quota. Even an ancestor outside the
chosen root's reachable subgraph appears when needed, including every other
parent branch of a shared descendant. Bindings appear once with normal
last-occurrence placement; complete parent records precede complete child records.

For example, given `A -> B -> C -> D -> E`:

- `query C --max-distance 0 --with-ancestors` matches C and reads A, B, C.
- `query C --max-distance 1 --with-ancestors` matches C, D and reads A, B, C, D.
- `query C --with-ancestors` still matches C's whole downstream subgraph first.

The letters above are schematic; real commands require full node IDs. Try
`specspec query 6EmKDz8= --max-distance 0 --with-ancestors` in this checkout for the
five bindings that justify left-to-right graph development. There is no separate
ancestor direction/mode or `context` command. With neither a root nor criteria,
query already reads the complete comparison, including distinct former roots;
`--with-ancestors` leaves that result unchanged. Empty matches add nothing.

Completed `selection` metadata includes `with_ancestors: true`, `matched_ids`, added
`ancestor_ids` and final `ids`, alongside the original `queries` and `population`.
Its preamble distinguishes match counts from additional ancestors; the final count
can exceed the rooted population. `surrounding` identifies omitted `child_ids`,
`sibling_ids` and their deduplicated `omitted_ids` union. These are direct children
and nodes sharing at least one direct parent with an **original match**, minus all
included bindings. Added ancestors do not expand the surrounding scope. Readable
output lists omitted IDs once, never their bodies. It is neighborhood information,
not another inherited requirement or a radius/depth filter.

Completion follows the same selected-record projection as the reading: target
parents/text for survivors, former parents/text for deleted records. A deleted
record can therefore reach a surviving ancestor's current binding. To read one
historical justification faithfully, select that revision explicitly, e.g.
`query ID --base REV --target REV --max-distance 0 --with-ancestors`. Original base
edges/records remain reconstructible; `boundary_parents` describes both original
revisions and can still contain an old external parent after completion.

One multi-source parent walk completes the union before one induced view and source
comparison. Including the manifesto can require evidence from other branches to
retain its global source-change badge; fewer printed bindings do not guarantee
proportionally fewer code reads. This is the same source contract as other queries.

Advanced `--max-bytes N` bounds the final UTF-8 result and its final LF, including
the JSON envelope or shared visible terminal-control escaping. Each response is
formatted once. An insufficient budget reports BUDGET without truncating any
binding or emitting a partial success result. Both presentations and JSON support
the same safeguard; query never silently shortens required context.

## Tree and node hints

Two-column rails (`│ │`, `├─requirement`, `└─↪`) continue through metadata and the
body line. Root metadata/body align at column zero, without an extra tree indent.
Headers give the lowercase type word, full node ID and all direct parents in
ascending full-ID order after ` @ `, separated by `, ` in both default and human
output, including the display parent. The ID names `.specspec/<id>.md`. Shared nodes, including deleted ones, have one full record at
their last conceptual unfolded occurrence; earlier occurrences are short `↪ ID ↓`
pointers. Iterative walks avoid recursion and exponential unfolding. The preamble
contains selected versions and applicable notes, with no abbreviation or `@` legend.

Unchanged headers have **no badge**. Changed headers use:

| Hint | Meaning |
| --- | --- |
| `added`, `modified`, `deleted` | Semantic node change |
| `source-changed` | Known source-contract change, including ancestors in both revisions |
| `file-only` | Literal-only node-file change, such as comments or EOL spelling |

`modified` can reflect body, parent or metadata changes. `file-only` is omitted when
a semantic hint already identifies a node change; `[source-changed file-only]`
can report both independent effects. Source-only changes never become fake node
modifications. Missing comparison evidence stays explicit in source rows, rather
than being mislabeled as a known `source-changed` change.

Every body uses the same untruncated one-line projection by default:

- Normalize CRLF to LF.
- Replace a single LF with one space, keeping adjacent words separate.
- Replace each run of two or more consecutive LFs with ` ¶ `.
- Apply the rule to leading/trailing runs too; retain every other character,
  including headless text, Markdown markers, indentation, tabs and trailing spaces.

This approximates Markdown soft breaks and paragraph separation, not full Markdown
rendering: lists, code and hard breaks are flattened by the same literal rule, and
whitespace between LFs interrupts a run. Original bodies remain exact in JSON and
node files; `diff` supplies literal changes. `--human` preserves logical body lines,
blank lines, indentation, tabs and trailing spaces instead of applying the one-line
projection. CRLF is normalized to LF for display. Both presentations use shared
visible terminal-control escaping and retain full content with no truncation.
Current format-version/extensions remain compact metadata. Selected bodies have no
quotation wrappers.

The display selects **current parents for current nodes and former parents for deleted
nodes**. Valid original graphs yield an acyclic projection. Invalid working
references can connect missing/deleted parents to survivors; cycle-safe walks show
all components with explicit missing endpoints. Lost old links among surviving
nodes remain in comparison JSON and `diff`. Each original graph is diagnosed
independently; the derived display may have new shortcuts, changed parent
types or distinct roots without becoming a new canonical graph or changing any files.

## Source contracts decide what counts as change

A source item shows its actual target location, or its base location for a removed
reference. By default, all items for a node share one `sources: ` line, separated by
`, `. `--human` puts each item on its own `sources: ` line. Both retain comparison
order, duplicate occurrences and every item's own declaration/issue hints.
Inclusive spans use `path:10-12,30-35`; a single line is `path:10`, and an empty text
file is `path:empty`. Range commas have no following space; unusual paths, including
commas, are quoted. Raw reference metadata and both locations remain complete in JSON.

**Permitted changes stay unmarked**, including in ancestor `source-changed` badges:

| Reference class | Permitted changes |
| --- | --- |
| Strict region | Reliable relocation, edits outside/between selections or at outer boundaries, logical EOL equivalence |
| Expanding region | The above, plus reliably mapped internal/contained edits and partial deletions with a surviving selection |
| Path-only whole file | Content changes; the contract requires a safe regular file, not stable contents or readable lines |

A changed byte, line count or coordinate is therefore not automatically a source
change. Whole-file binary/LFS/large artifacts need no line warning merely because
optional line coordinates cannot be read. Quiet means the reference permits the
change, not proof that the code still fulfills its intention.

Relevant hints include:

- `ref+` / `ref-`: reference occurrence added/removed, independently of code edits.
- `conflict` / `missing`: a broken reference, such as a strict internal edit or lost selection/file.
- `restored` / `file added`: a known broken-to-valid transition.
- `ambiguous` / `unavailable`: uncertainty; a `base` or `target` prefix identifies the other side where needed.

Known valid/broken transitions produce `source-changed`. A persistent missing link or identical
broken mapping remains visibly problematic but is not a new revision change.
Unknown mappings do not become fake changed/unchanged verdicts. Partial strict
fragments never stand in for a complete trusted selection.

Every exact union reference in the required evidence scope is checked against both
selected code versions, even
when only one node declares it. Unequal declarations stay removals/additions, not
guessed pairings by path or symbol. Duplicates remain separate rows. Comparisons
use both versions, rather than treating an older anchor's `modified` outcome as a
new change. See [source regions](source-regions.md) for the shared resolver contract.

JSON `source_resolutions[].contract` is `same`, `changed` or `unavailable` for this
contract comparison. `source_contract_affected` drives `source-changed` and query affected scope;
`source_contract_complete` reports comparison completeness. Existing byte/text/
position/region facts and conservative `source_changes`/`source_affected` remain raw
review evidence, not query change badges. Other inspection/preview/check commands
retain their contextual outcomes and conservative file-impact behavior.

## Versions, details and safety

`--base` defaults to fresh `HEAD`; `--target` defaults to `workspace`. Committed refs
are pinned without checkout. Workspace means saved files, not unsaved buffers/forms.
A missing base specification or genuinely unborn HEAD has an explicit empty base.
A non-Git workspace identifies its synthetic empty graph and unavailable base code.
Unavailable refs fail explicitly. Diagnosable graph-invalid inputs remain readable;
partial parsed content retains available evidence with a nonzero result rather than
fabricated complete scope. Unsupported schemas remain unsupported. Node format and
application API are **7**. See [invalid-state inspection](invalid-graphs.md) for
`query --issues --with-ancestors`, contextual diffs and metric availability.

`query --json` retains target/before records, original edge deltas, file-change
summaries, refs/commits and full derived source facts for the selected scope. `--human --json` produces the
same structured output as `--json`: human changes only the text presentation.
Exact patches belong to
`specspec diff`, or `specspec diff BASE TARGET` for the matching committed comparison.

One rooted graph batch shares minimum/maximum distance propagation and reverse
integer-bitset influence counts across all criteria. It releases child bitsets after
their last parent consumes them, without per-node closure searches or path unfolding.
Metric ranking agrees with a child-frontier priority walk; thresholds filter before
sorting and percentage quotas use bounded top-k selection. Projection, revision
reads and source comparisons run once, not once per metric.

Known committed source blobs/anchors fill the existing per-call cache in batches;
identical selected commits share a code reader. Every invocation resolves refs and
saved files freshly, without a persistent or cross-call cache. Workspace bytes never
come from index entries. See [profiling and local measurements](investigations/query-performance.md).

Queries never save, reanchor, stage, commit, write objects/refs, fetch or install
hooks. Shared resolver budgets/caches remain in force; source uncertainty does not
discard a valid graph reading. Cached workspace reads are not an atomic cross-file
snapshot when another process edits files concurrently.

# Read current specifications with change hints

```sh
specspec query                                      # Fresh HEAD → saved workspace
specspec query --human                              # Multiline bodies, individual sources
specspec query --base release --target workspace
specspec query --base main~2 --target main
specspec query --json
```

`query` is always a revision comparison, like [spotlights](spotlights.md), but its
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

## Tree and node hints

Two-column rails (`│ │`, `├─requirement`, `└─↪`) continue through metadata and the
body line. Root metadata/body align at column zero, without an extra tree indent.
Headers give the lowercase type word, filename stem and all direct parents in
ascending full-ID order after ` @ `, separated by `, ` in both default and human
output, including the display parent. The stem names
`_specspec/<stem>.md`. Shared nodes, including deleted ones, have one full record at
their last conceptual unfolded occurrence; earlier occurrences are short `↪ ID ↓`
pointers. Iterative walks avoid recursion and exponential unfolding. The preamble
contains selected versions and applicable notes, with no abbreviation or `@` legend.

Unchanged headers have **no badge**. Changed headers use:

| Hint | Meaning |
| --- | --- |
| `added`, `modified`, `deleted`, `renamed` | Semantic/path node change; renamed is filename-only |
| `source-changed` | Known source-contract change, including ancestors in both revisions |
| `file-only` | Literal-only node-file change, such as comments or EOL spelling |

`modified` can reflect body, parent or metadata changes. `file-only` is omitted when
a semantic/path hint already identifies a node change; `[source-changed file-only]`
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
Current format-version/extensions remain compact metadata. There are no node filters
or body quotation wrappers.

The display selects **current parents for current nodes and former parents for deleted
nodes**. It is acyclic: a current node cannot have a deleted parent. Lost old links
among surviving nodes remain in comparison JSON and `diff`. Each original graph is
validated independently; the derived display may have new shortcuts, changed parent
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

Every exact union reference is checked against both selected code versions, even
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
Invalid refs/schemas fail before output. Node format and application API remain **6**.

`query --json` retains target/before records, original edge deltas, file-change
summaries, refs/commits and full derived source facts. `--human --json` produces the
same structured output as `--json`: human changes only the text presentation.
Exact patches belong to
`specspec diff`, or `specspec diff BASE TARGET` for the matching committed comparison.

Known committed source blobs/anchors fill the existing per-call cache in batches;
identical selected commits share a code reader. Every invocation resolves refs and
saved files freshly, without a persistent or cross-call cache. Workspace bytes never
come from index entries. See [profiling and local measurements](investigations/query-performance.md).

Queries never save, reanchor, stage, commit, write objects/refs, fetch or install
hooks. Shared resolver budgets/caches remain in force; source uncertainty does not
discard a valid graph reading. Cached workspace reads are not an atomic cross-file
snapshot when another process edits files concurrently.

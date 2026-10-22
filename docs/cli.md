# Compact command interface

One CLI serves people and coding agents. Default output is readable text/Markdown;
`--json` explicitly selects compact UTF-8 API **6**. Redirection does not change the
format. Canonical node format is **7**; upgrade the CLI and both host builds
together. The CLI does not supply old command aliases or old protocol readers.

## Eight everyday commands

```sh
specspec init manifesto.md                 # New project only; - reads UTF-8 stdin
specspec show                              # IDs/types/headings, not every body
specspec show <full-id>                     # Complete node metadata and binding text
specspec show <full-id> --dependents        # Structural potential impact
specspec query                            # Complete HEAD → workspace tree comparison
specspec query --base main~2 --target main # Explicit versions, like spotlights
specspec query --human                   # Original body lines, individual sources
specspec query --max-distance 2          # Root plus inclusive longest-path levels
specspec query --max-distance 50%        # Metric-priority half of reachable nodes
specspec query <full-id> --influence 5   # Rooted subgraph; influence >= 5
specspec query --min-distance 25% --influence 25% # Independent selections, union
specspec query <full-id> --max-distance 0 --with-ancestors # Node + every ancestor
specspec query <full-id> --max-distance 2 --with-ancestors # Branch slice + ancestors
specspec add --parent <id> --body node.md
specspec update <id> --body revised.md
specspec delete <id> --dry-run              # All descendants, including shared ones
specspec delete <id> --yes                  # Explicit consent; warnings remain
specspec check                             # Saved graph/schema and ordinary warnings
specspec check --staged --sources           # Exact index plus source mapping/retention
specspec diff                              # Full HEAD → workspace review
specspec diff <base> <target>               # Historical comparison, no checkout
```

`--root <project>` precedes the command. IDs include their final `=` and are
case-sensitive. Hyphen-leading IDs remain accepted as full node arguments.
`add --type implementation` selects an implementation leaf. Repeated `--parent`
values specify the complete replacement set on update. The manifesto keeps its
empty parents; ordinary nodes require parents. Bodies are files or `-` stdin,
not shell-interpolated inline program text. The complete candidate must be shortcut-free:
no direct parent may already be an indirect parent. REDUNDANT_PARENT reports the
affected edge and alternative path, including redundancies on other nodes after an
update. Related multi-file Markdown changes must be made coherently and checked;
managed writes never normalize them. See [graph structure](graph-structure.md).
Init and add create `_specspec/<id>.md`, including the ID's trailing `=`.
Paths depend only on identity; headings and binding text remain inside the document.

`query` is always a revision comparison: fresh `HEAD` to saved `workspace` by default,
with spotlight-style `--base` and `--target` options. Current records use current
parents; deleted records use former parents and old text in the same reading.
Ascending-ID last-occurrence placement and short `↪ ID ↓` references keep sharing
compact. Two-column rails frame full parent headers and one-line body readings;
root content has no extra indent. Single newlines become spaces and longer runs
become ` ¶ `. Types and change hints use lowercase words: `added`, `modified`,
`deleted`, `file-only` (literal changes) and `source-changed` (known
contract changes, including ancestors). There is no legend. Edits allowed by
strict/expanding/path-only references stay quiet.
Parent headers always separate full IDs with `, `. Default source items share one
`sources: ` line with comma-space separators, preserving duplicates and individual
broken/uncertain/restored hints. `--human` keeps logical body lines and lists source
occurrences individually, without changing parents, source facts or revision selection.
`query --json` retains reconstructible API-6 records and complete source facts, with
file-change summaries rather than patches. Use `diff` for exact text modifications.
Original body layout remains in JSON and node files. `--human --json` is identical
to `--json`. Optional `query [NODE_ID]` starts at that current/deleted node, otherwise
metric selections start at the target manifesto. `--min-distance`/`--max-distance`
admit values <= their integer cutoff; `--influence` admits self-inclusive counts >=
its cutoff. Percentages select a rounded-up share of the root's reachable population,
with ID tie-breaks. Each criterion selects independently; combine by union. Scoped
JSON identifies selected IDs, metric values, boundary parents and necessary source
evidence. `--with-ancestors` completes the matched set through every parent path
without changing its metrics, population or quotas. JSON separates `matched_ids`
from added `ancestor_ids`; final `ids` include both. Omitted direct children and
siblings of the matches are identified separately by ID, without their bodies.
Added ancestors do not expand that surrounding scope. An unfiltered complete query
already contains every ancestor, so completion is a no-op there.
Advanced `--max-bytes N` bounds the actual encoded query result plus its final
newline, including the JSON envelope or visible terminal escaping. Insufficient
budgets fail without truncation or a partial success result. See
[query selection and source hints](query.md).

Mutations print changed IDs/paths and potential affected scope, not an entire graph.
Human diagnostics go to stderr; JSON diagnostics are structured in its one envelope.
Terminal control characters in project text are displayed visibly, not executed.
Read-only exploration does not stage, commit, install hooks or fetch source objects.

## Full review diff

Diff groups nodes by stable ID and readable heading, identifies type/parent/source/
metadata changes, and shows **all changed canonical-file hunks** including YAML,
body text, comments, whitespace, line endings and final newlines. Added/deleted files
are shown completely. A relationship overview labels both ends with full IDs/titles.
`diff --summary` is explicitly abridged; it is not the default. Git supplies directly
applicable byte patches. Linked-code file impact is a separate informational section,
not a fabricated node M and not a dump of implementation code. Invalid/unavailable
comparisons receive diagnostics/incomplete impact rather than a false empty result.

## Structured results

```json
{"api_version":6,"ok":true,"result":{"node_count":22},"diagnostics":[]}
```

Show without an ID returns complete normalized node records in JSON; parents encode
relationships without a redundant edges array. Mutation receipts return changed IDs,
ID/path nodes and affected IDs. Delete additionally retains its complete assessed plan.
Node-record bodies use LF normalization; canonical files and native before/after plans
preserve their original body/EOL bytes. Full diff patches expose literal file changes.

Comparison JSON contains one `target` snapshot, base metadata, a `before` array of
previous records only for differing/deleted nodes, ID-based `changes`, added/removed
relationships, file/source impact, refs and resolved commit addresses. Reconstruct base
by excluding added IDs from target records and overlaying every `before` record.
Unchanged records are shared logically. A loaded UI result already has `snapshot`,
so its compact `diff` omits the duplicate target. The shared adapter reconstructs the
complete individual revisions for the renderer; a display union is not itself the DAG.
HEAD is resolved afresh: D ghosts survive staging and disappear after commit.

Exit status: 0 successful operation, 1 validation/rejected action, 2 invocation/I/O.
Native read/plan operations may succeed while reporting an invalid repairable graph.
There is no automatic human/JSON choice based on TTY, and no LLM/UI JSON dialect flag.

## Advanced tools and integration

`sources show [ID]` inspects mappings; `--source N` opens the Nth literal preview.
`sources capture` and `sources reanchor` retain deliberate strict/expanding decisions,
`--range`, `--ref`/`--staged` and non-writing `--dry-run`. See [source regions](source-regions.md).
`check [ID] --sources` checks all or selected source mappings; staged checks use exact
index graph/code. `recover` restores recognized interrupted transaction states;
`--force-lock` is only for a confirmed absent writer. See [deletion/recovery](deletion.md).

`spotlight add NODE_ID... MESSAGE [--base REV] [--target REV|workspace]` adds a
color-free comparison spotlight. IDs may include deleted or unchanged members.
Explicit Git refs pin commits; the implicit default follows live HEAD → workspace.
`spotlight show [SHOT_ID]` reports each record's own A/M/D/= statuses and advisory
workspace drift. Only uncommitted workspace nodes have saved checksums; Git owns
committed text and no node copies are retained. `spotlight flush --yes` explicitly
clears local metadata and obsolete copies. See [local spotlights](spotlights.md)
for complete structures, warning behavior, native-buffer boundaries and UI selection.

Advanced source-array `--sources`, source `--symbol`/`--replace`,
mixed metadata `--graph-ref` and `delete --reviewed-plan FILE|-` remain available
without bloating everyday help. Reviewed deletion plans are rechecked under lock;
plan transport does not waive warnings, native dirty guards or original-byte checks.

The hidden `api` operation consumes bounded JSON stdin and returns one API-6 envelope.
Requests require integer `api_version: 6` and `op` from `read`, `plan`, `source-view`,
`source-capture`, `annotations`, `annotation-create`, `annotation-flush`. Both hosts use `read` with optional `base`/historical `target`;
VS Code additionally supplies `documents`. `plan` requires an `edit` and never writes
files. Source operations inspect/capture into forms without persisting them.
Internal operation names are independent of public `spotlight` naming.
`annotations` reads the shared local spotlight list independently of graph validity;
`annotation-create` takes `message`, `nodes` and trusted comparison/native inputs.
`annotation-flush` requires the reviewed shot-ID list in `expected`; hosts confirm
first. Working comparison reads supply sparse `workspace_state` for advisory drift
warnings, outside canonical node records. Unknown fields/operations fail. Bounded cache hints are verified against current Git objects;
they are stripped from renderer data and never authorize a write. Inputs are bounded
at 16 MiB, node files at 1 MiB; the UI bridge retains its existing process/output limits.

Git hook/CI setup is owner-controlled. Put `specspec check --staged` (optionally
`--sources`) in your existing hook framework or manually managed hook; preserve its
other commands and executable/environment selection. SpecSpec does not install or
replace hooks. The public read interface uses `query` for ancestor context; no
`context`, `hook`, `list`, `impact`, `validate`, `export` or public `editor` command remains. Mermaid export is not part of this two-representation CLI.

The original owner source in root `AGENTS.md` and `INTENTION_SPEC.md` is preserved.
Use this guide and [the current graph tour](own-spec.md) for today's operational
commands where older examples in preserved owner input name superseded commands.

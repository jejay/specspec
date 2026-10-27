# Compact command interface

One CLI serves people and coding agents. Default output is readable text/Markdown;
`--json` explicitly selects compact UTF-8 API **7**. Redirection does not change the
format. Canonical node format is **7**; upgrade the CLI and both host builds
together. The CLI does not supply old command aliases or old protocol readers.

Every root, command and subgroup `--help` supplies detailed task explanations,
complete examples, defaults, input meanings and effects. Help is static: it opens
no project and consumes no stdin. Source/spotlight groups keep their own inspection
subcommands; the sole top-level specification-reading command is query.

## Seven everyday commands

```sh
specspec init -m "# Product intention" -m "Explain the goal." # New project only
specspec query <full-id> --max-distance 0   # One complete binding
specspec query <full-id>                    # Its complete descendant scope
specspec query <full-id> --raw --json       # Literal document for repair
specspec query                            # Complete HEAD → workspace tree comparison
specspec query --base main~2 --target main # Explicit versions, like spotlights
specspec query --human                   # Original body lines, individual sources
specspec query --max-distance 2          # Root plus inclusive longest-path levels
specspec query --max-distance 50%        # Metric-priority half of reachable nodes
specspec query <full-id> --influence 5   # Rooted subgraph; influence >= 5
specspec query --min-distance 25% --influence 25% # Independent selections, union
specspec query <full-id> --max-distance 0 --with-ancestors # Node + every ancestor
specspec query <full-id> --max-distance 2 --with-ancestors # Branch slice + ancestors
specspec add --parent <id> -m "# Conclusion" -m "Explain the reasoning."
specspec update <id> -m "# Revised conclusion" -m "Its current reasoning."
specspec update <id> --replace "old passage" "new passage" # Exact body edit
specspec delete <id> --dry-run              # Exact files, retained reference faults
specspec delete <id> --yes                  # Warned selected-file consent
specspec query --issues --with-ancestors    # Broken justification and downstream context
specspec diff --with-context               # Earlier/current bindings and cause evidence
specspec update <id> --parent <id> --require-valid # Require the whole final graph valid
specspec check                             # Saved graph/schema and ordinary warnings
specspec check --staged --sources           # Exact index plus source mapping/retention
specspec diff                              # Full HEAD → workspace review
specspec diff <base> <target>               # Historical comparison, no checkout
```

`--root <project>` precedes the command. IDs include their final `=` and are
case-sensitive. Hyphen-leading IDs remain accepted as full node arguments.
`add --type implementation` selects an implementation leaf. Repeated `--parent`
values specify the complete replacement set on update. The manifesto keeps its
empty parents; ordinary nodes require parents. `-m/--message` supplies literal body
text. Repeated values join with one blank line, without trimming supplied whitespace
or applying Git message cleanup. Logical line boundaries are preserved; their encoding
follows the existing document's style, or LF for a new node.
Markdown headings, Unicode and actual newlines remain text. `-` and filenames are
literal text too; backslash-n is not automatically expanded. Quote for your shell;
programmatic callers should pass an argument array with no shell. Omitting body-edit
inputs on update leaves the body unchanged; explicit empty text is an explicit schema-checked
edit. No editor opens implicitly. A completed valid graph is shortcut-free:
no direct parent may already be an indirect parent. Graph-invalid intermediate edits
are saved with explicit validity/completeness diagnostics; --require-valid checks the
whole final candidate before any writes. The starting graph need not be valid. REDUNDANT_PARENT reports the
affected edge and alternative path, including redundancies on other nodes after an
update. Related multi-file Markdown changes must be made coherently and checked;
managed writes never normalize them. See [graph structure](graph-structure.md) and
[invalid-state inspection/repair](invalid-graphs.md).
Init and add create `.specspec/<id>.md`, including the ID's trailing `=`.
Paths depend only on identity; headings and binding text remain inside the document.

## Replace selected body text

Use repeatable `update --replace OLD NEW` to edit passages without resending the
whole body:

```sh
specspec update NODE_ID \
  --replace "old wording" "new wording" \
  --replace "another old passage" "replacement passage"
```

Each nonempty `OLD` needs **exactly one original-body match**, including all permitted
newline layouts. LF, CRLF and bare CR compare equally. Ordinary Markdown paragraph
soft breaks can match one ASCII space, in either direction: `a long` followed by a
soft newline and `sentence` can be selected with `"a long sentence"`. This is the
default behavior of the same option; no additional match options are needed.

Words, case, Unicode normalization, punctuation, other spaces and indentation stay
literal. Paragraph boundaries, headings, table rows, code, HTML syntax, list markers
and explicit hard breaks retain their structure. Only source-mapped paragraph soft
breaks participate; container prefixes/continuation indentation are not stripped to
force a match. Missing/multiple matches, including overlapping occurrences, reject
the whole invocation. An exact-layout match does not win over another admissible
wrapped occurrence. Supply context to disambiguate.

All pairs refer to the same original body, never preceding insertions, and their
actual matched ranges must be disjoint. NEW retains literal content; empty NEW
deletes the passage. Newline encoding follows the target document, independently of
Git settings. Equal OLD/NEW can change a tolerantly matched prose wrap. Unmatched
logical characters, indentation, spaces and blank lines stay exact;
there is no whole-body reflow, regex, fuzzy spelling or backslash-n expansion.
The resulting node must satisfy the ordinary schema and size limits. Raw JSON
(`query NODE_ID --raw --json`) remains available for exact document text and structure.
Frontmatter is outside the matching surface; parent/source flags retain their
separate meanings and can accompany replacements.

Replacement input is mutually exclusive with `-m/--message` and integration `--body`
within that update. Whole-body inputs remain available for substantial rewrites.
Replacements work in ordinary editing chains and support `--dry-run` and
`--require-valid`. Syntax, source conflicts and input limits are checked before
body-file/stdin reads. Actual matching happens under the writer lock on fresh saved
body text; stale matches fail before any canonical writes. This is context matching,
not a claim that unrelated text or its meaning has stayed unchanged.

There are at most 1024 replacement pairs across the invocation. OLD and NEW both
count toward the 16 MiB aggregate authoring-text budget alongside other body inputs;
each replacement value and resulting canonical node has a 1 MiB limit. Arguments
also retain their separate budget and smaller OS limits. Quote both values for your
shell (the examples use Bash/Git Bash); programmatic callers should use an argument
array. `--replace=OLD NEW` is also accepted; the attached spelling supplies only OLD.
Markdown/candidate analysis has bounded work guards; exceeding them rejects the
whole invocation explicitly rather than guessing uniqueness. Full-body input stays
available. See [matching and verification details](investigations/exact-replacements.md).

## Compose editing commands

Repeat or combine **only `add`, `update` and `delete`** in one invocation. Each step
uses its ordinary options; the complete invocation produces one explicit candidate,
one receipt and one recoverable transaction. For example, in Bash/Git Bash (replace
the uppercase placeholders with existing full IDs):

```sh
specspec delete OLD_ID \
  add --as goal --parent EXISTING_ID -m "# New conclusion" \
  add --as detail --parent '$goal' -m "# Its detail" \
  update SURVIVING_ID --parent '$goal' --parent OTHER_ID \
  --require-valid --yes --json
```

- `add --as NAME` defines a local new-node alias. `--parent '$NAME'` references its
  generated ID; forward references work too. Names start with an ASCII letter,
  followed by up to 63 ASCII letters, digits, underscores or hyphens. Quote the
  dollar sign for your shell. The response's `result.aliases` maps names to full IDs.
- Each `update` names one existing node. `delete` still accepts multiple IDs, and
  either command may repeat. An update's `--parent` values replace its entire list.
  Configure new nodes completely in their `add` step: aliases are parent references,
  not instructions to update/delete a just-added node. One identity gets one edit;
  duplicate aliases and conflicting/duplicate target edits are rejected. Use repeated
  `--replace OLD NEW` pairs within one update for several passages of the same node.
- `--dry-run`, `--require-valid`, `--yes` and `--json` apply to the **whole invocation**,
  wherever supplied. The validity boundary checks the final candidate, not temporary
  per-step states. Preview IDs are not reserved; re-running creates fresh IDs.
- All steps are parsed before body-file/stdin reads or writes. Read/init/source/
  spotlight/recovery/API commands cannot join an editing invocation. For example,
  `update ID -m "..." query ID delete OTHER_ID` fails without partial edits.
  Command names supplied as option values, such as `-m "delete"`, remain literal.
- A singleton `add --as NAME` returns its alias too. `add` and `update` now support
  `--dry-run` as well as `delete`. Existing ordinary single-edit result contracts
  remain unchanged when these new capabilities are not requested.

There is no separate `apply` command or JSON/file/stdin batch-plan input. Chains
contain 1–1024 editing steps, with arguments and aggregate body input each bounded
at 16 MiB and every canonical node still bounded at 1 MiB. Smaller shell/OS argv
limits still apply. See [coherent repair](invalid-graphs.md#one-coherent-multi-node-change)
and [verification boundaries](investigations/editing-chains.md).

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
`query --json` retains reconstructible API-7 records and complete source facts, with
file-change summaries rather than patches. Use `diff` for exact text modifications.
Parsed JSON preserves logical body layout with CRLF/CR normalized to LF. Raw query
retains physical documents; normal diffs compare logical newline boundaries. `--human --json` is identical
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

Query remains usable with graph errors. `query --raw` (with an ID or direct
`--path`) reads literal malformed documents; `--target REV` selects committed bytes
and `--staged` selects exact index bytes. Raw mode is separate from a parsed graph
comparison: reject `--base`, metrics, ancestors, issues or human presentation there.
`--path` and `--staged` require `--raw`. `query --issues` selects structural findings and their
potential descendants, optionally completed by `--with-ancestors`; use it without
metric criteria. Cycles/disconnected components remain visible and finite. Undefined
cyclic maximum-distance requests fail explicitly. Partial parsed scope is not a
fabricated successful metric selection. Missing endpoints and historical bindings
have distinct meanings.

## Full review diff

Diff groups nodes by stable ID and readable heading, identifies type/parent/source/
metadata changes, and shows **all changed logical canonical-text hunks** including
YAML, body text, comments, whitespace and final-newline presence. Added/deleted files
are shown completely. A relationship overview labels both ends with full IDs/titles.
`diff --summary` is explicitly abridged; it is not the default. Git supplies directly
applicable byte patches. Linked-code file impact is a separate informational section,
not a fabricated node M and not a dump of implementation code. Declared-reference
changes remain distinct from references becoming unresolved. Graph validity and
comparison completeness are independent. Unreadable files are unavailable, not
fabricated node deletions. Incomplete comparisons retain evidence with nonzero status.

`diff --with-context` adds deduplicated before/current bindings, surviving parent and
ancestor context, potential descendants and finite cause paths from both graphs.
Repeated `--node ID` focuses it; advanced `--max-bytes N` bounds the actual encoded
result. Context supplies evidence, never a determination of owner motive or semantic
justification. Full canonical patches remain present unless --summary is explicit.

## Newlines independent of Git configuration

LF, CRLF and CR represent the same logical node line boundaries. Reads and normal
diffs ignore encoding-only differences without changing saved files. Diff patches
use logical LF lines and omit the newline-counter dump. Words, case, indentation,
trailing spaces, blank-line counts and EOF termination remain significant; EOF
changes use ordinary patch markers. `query --raw` supplies exact physical bytes.

Existing-document managed writes and native plans retain the newline convention
of the opening frontmatter delimiter; new nodes use LF. Every complete node written
or planned by these tools ends with a newline: append one in the document's style
only when missing, preserving existing trailing spaces and blank lines. This also
applies to message/file/stdin body inputs, replacement NEW and metadata-only edits. Actual serialized byte limits
still apply. Original-byte checks, journals, recovery and immutable Git objects
remain byte-exact. Linked source files keep their own formatting and contracts.

Unterminated manual/historical nodes remain readable and valid; reads and raw-editor
saves are not formatting passes. An explicit tool write adds a missing terminator,
which remains visible as an EOF change. No Git settings, attributes, hooks or index
entries are installed or changed to implement this policy. It works with repository/user checkout settings as they are;
no repo-specific clean/smudge filters run for application text normalization.

## Mutation receipts

Default mutation output identifies nodes, rather than their backing Markdown files.
Each nonempty action group occupies one unpadded line, with full IDs separated by
comma-space:

```text
Added: kPmrkZI=, AbcDefA=
Modified: LmnOpqA=
Deleted: RstUvwA=
```

`init` reports its first node under `Added` too. Updates whose proposed logical text
matches the saved logical text report `Unchanged`, including encoding-only changes.
Body, parent, source and selected-passage updates use the same rule. These labels
compare the invocation's locked original and candidate contents, independently of
Git status against HEAD. Groups appear in Added/Modified/Deleted/Unchanged order;
IDs retain the writer's target order within each group.

Dry runs use `Would add`, `Would modify` and `Would delete`; equal logical text still
report `Unchanged`. Generated preview IDs remain unreserved. A rejected operation
prints diagnostics rather than a completed-change summary. A deletion requiring
consent can show its `Would delete` proposal while refusing to remove anything.

Requested `--as` aliases have one unpadded, comma-separated `Aliases` line mapping
local names to full IDs. Those associations, structural references, instruction
creation/preservation, potential affected scope, validity and completeness add
meaningful context separately. Diagnostics can still identify actual file paths.
JSON retains its existing ID/path records and selected `changed_ids`, including
no-op update targets; the text action groups do not add protocol fields.

## Structured results

```json
{"api_version":7,"ok":true,"result":{"node_count":22},"diagnostics":[]}
```

Query JSON returns complete normalized selected target/before records; parents encode
relationships without a redundant edges array. Mutation receipts return changed IDs,
ID/path nodes and affected IDs. Delete additionally retains its complete assessed plan.
Node-record bodies use LF normalization. Raw documents and native before/after plans
retain physical evidence. Full diff patches expose logical canonical-text changes;
existing structured patch records retain physical layout metadata where applicable.

Comparison JSON contains one `target` snapshot, base metadata, a `before` array of
previous records only for differing/deleted nodes, ID-based `changes`, added/removed
relationships, file/source impact, refs and resolved commit addresses. Reconstruct base
by excluding added IDs from target records and overlaying every `before` record.
Unchanged records are shared logically. A loaded UI result already has `snapshot`,
so its compact `diff` omits the duplicate target. The shared adapter reconstructs the
complete individual revisions for the renderer; a display union is not itself the DAG.
HEAD is resolved afresh: D ghosts survive staging and disappear after commit.

Exit status: 0 successful operation, 1 validation/rejected action, 2 invocation/I/O.
Reads and mutations can succeed while reporting an invalid repairable graph.
`ok`/exit zero means the requested operation was delivered, not structural validity.
Mutation receipts include `applied`, `graph_valid` and `analysis_complete`; check
remains strict. Error diagnostics can describe a saved intermediate graph without
meaning its transaction failed. See [invalid-graph examples](invalid-graphs.md).
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

### Integration-only bulk inputs

Ordinary help focuses on literal messages and composed editing steps. Explicit
hidden inputs remain for bulk body automation and the existing visual hosts:

- `init/add/update --body FILE|-` reads UTF-8 body bytes from a file or stdin.
  File paths resolve from the launch directory. Editing steps can each name a body
  file; at most one step may consume stdin. `init` remains standalone.
- `--message`, `--body` and update's `--replace` are mutually exclusive on each step.
  All such conflicts fail before body reads or canonical writes. Positional init payloads are
  rejected rather than interpreted as body text.
- Hidden `--parents-json` and `--sources` keep their existing integration meanings.
- Reviewed deletion-plan stdin and the private API channels are unchanged. A reviewed
  plan binds one standalone `delete`; combining it with editing steps is rejected
  before reading the plan. Use the complete chain's `--dry-run` for a chained preview.
  Managed UI saves still send body stdin; native VS Code saves retain their document
  owner. The UI uses neither chained edits nor a JSON batch-plan transport.

Node files remain bounded at 1 MiB and bulk requests at 16 MiB. Operating-system and
shell argument limits are smaller and independent: Windows CreateProcess permits
32,767 UTF-16 units for the whole command line including its terminator; cmd.exe
permits 8,191 characters. Quotes/other arguments consume that budget too. Unix has
platform-specific argument/environment limits. A long argv can fail before SpecSpec
starts; repeated options do not bypass the total. Use the explicit bulk interfaces
for large bodies. There is no automatic fallback, truncation or batch splitting.
Command text may appear in shell history/process arguments. Shell quoting differs
between Bash, PowerShell and cmd; the chain examples use Bash single quotes.
PowerShell native-argument quoting also depends on its version/passing mode.

### Private application transport

The hidden `api` operation consumes bounded JSON stdin and returns one API-7 envelope.
Requests require integer `api_version: 7` and `op` from `read`, `plan`, `source-view`,
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

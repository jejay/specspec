# Implementation source regions

Implementation `sources` supports whole-file hints and Git-addressed text regions.
Canonical **node format 6** and **application API 6** retain the source-region
contract, with a compact current command surface.
Node IDs still use five random bytes and padded Base64url, including `=`.

```yaml
sources:
- path: src/example.py
  symbol: human description, not an AST query
  blob: 0123456789abcdef0123456789abcdef01234567
  mode: strict
  ranges:
  - [100, 150]
  - [300, 500]
- path: src/other.py
  blob: 89abcdef0123456789abcdef0123456789abcdef
  mode: expanding
  ranges:
  - [13, 15]
- path: image.png
  symbol: whole-file reference; no line anchor
```

The hashes above are illustrative. Capture real full object IDs through the tool.
For anchored entries, `blob`, `mode` and `ranges` are required together. Intervals
are 1-based, inclusive, sorted and nonoverlapping (maximum 64 per reference).
Full lowercase SHA-1 and SHA-256 Git IDs are supported. No shortened IDs, absolute
paths, traversal or canonical resolution/approval state is stored.

## Two meanings of a region

| Change | Strict (specific) | Expanding (broad) |
| --- | --- | --- |
| Lines inserted before a region | Relocate | Relocate |
| Insertions strictly inside its bounds | Conflict; don't absorb new lines | Include them; report modification |
| Replacement wholly inside | Conflict; preserve surviving original fragments | Include replacement; report modification |
| Insertions exactly at outer bounds | Exclude | Exclude |
| Insertions in a gap between separate regions | Exclude | Exclude |
| Deleted content | Conflict/missing | Modified/missing |
| Replacement crossing a region boundary | Conflict or ambiguity | Ambiguity rather than guessing bounds |
| Uniquely identifiable move/rename | Relocate with evidence | Relocate with evidence |
| Copies, unclear boundaries, unavailable history | Report ambiguity/unavailability | Report ambiguity/unavailability |

Ranges are against an **immutable source snapshot**. Present positions are derived;
mechanical offsets do not rewrite the spec. Strict is a source-reference contract,
not an editing prohibition or node acceptance gate. Expanding permission to include
new code is not proof that it still implements the explanation. Separate gaps are
never silently swallowed. Runtime outcomes (`resolved`, `modified`, `conflict`,
`missing`, `ambiguous`, `unavailable`, or whole-file `file`) are not canonical statuses.

Git diffs and bounded textual context assist mapping. An unchanged uniquely matched
block may follow an intra-file move; duplicate original/surviving blocks can be
ambiguous. Git rename evidence and exact blob candidates help locate renamed files.
A blob contains no path or ancestry, so copies cannot establish file identity.
This is heuristic navigation/review context, not semantic code tracking.

## Capture and explicitly correct

Default capture uses committed **HEAD**. Use `--ref <revision>` for another committed
source or `--staged` for exact index content. Capture/reanchor do not stage source,
write Git objects/refs, commit, or install hooks.

```sh
specspec sources capture <implementation-id> src/example.py \
  --range 100:150 --range 300:500 --mode strict --ref HEAD

# New code can be referenced in the same commit without knowing that commit's ID:
git add src/other.py
specspec sources capture <implementation-id> src/other.py \
  --range 13:15 --mode expanding --staged
# Review/stage the changed spec node normally; don't forget the source file.

specspec sources show <implementation-id>
specspec sources show <implementation-id> --source 1
specspec check <implementation-id> --sources --json
specspec sources show --staged --json
specspec sources show --ref <revision> --json
```

Source inspection/checks default to working graph/files. `--staged` reads **both metadata and
code from the index**; `--ref` reads both from that revision. `--graph-ref` can
explicitly select different committed metadata. Selecting historical code for
capture does not require an obsolete node-schema reader: the live node is current.

```sh
specspec sources reanchor <implementation-id> --source 1 --staged
# Conflicting/ambiguous ranges require deliberate replacements:
specspec sources reanchor <implementation-id> --source 1 \
  --staged --range 20:35
```

Source numbers are 1-based in the canonical JSON source ordering. Reanchor keeps
mode/description, updates blob/path/ranges only after an explicit command and never
approves implementation meaning. `capture --replace N` replaces a selected source;
otherwise capture appends. `--dry-run` on capture/reanchor returns metadata without
canonical writes. Ordinary writes use the existing lock/journal/byte transaction.

## Durability and checks

**Text containing an object ID is not a Git reachability edge.** Anchor only versions
already retained by commits or the staged source tree that will enter the upcoming
commit. If code is restaged to different bytes before committing, a new uncaptured
blob can become unreachable. Old references must remain available through retained
history; shallow clones or rewritten histories can lose them. Do not silently
substitute another source version. No custom retention refs or orphan-object
creation are implemented.

```sh
specspec check --staged --sources --json
```

This optional check inspects exact staged nodes, staged source bytes and retention.
It reports strict conflicts/missing/ambiguous/unavailable links with nonzero exit.
Expanding modifications remain reported but don't fail this contract check. Default
`check --staged` checks graph/schema only. Owner-controlled Git hooks or CI can
invoke it; SpecSpec does not install or replace hooks.

Whole-file source impact reporting remains conservative. A change outside a linked
region may alter imports, callers or other semantics; region mapping is **not** a
complete dependency analysis or reason to silently narrow review impact.

## Revision-comparison query

`specspec query` defaults to HEAD versus saved workspace; `--base` and `--target`
select other versions. Its source rows resolve every union declaration against both
code versions, independently of whether that exact reference occurs in both node
versions. The reference class determines change cues: strict accepts relocation and
outside/gap/boundary edits; expanding also absorbs reliably mapped contained edits;
path-only whole-file hints permit content changes and require a safe regular file.
Permitted changes add no source hint or source-changed badge. Binary/LFS/large whole files need
no spurious line warning because that class does not require readable lines.

Known valid/broken transitions, including restoration, drive source-changed and ancestors in
both original graphs. Missing/strict-conflicting links and ambiguous/unavailable
mappings stay visible. An existing problem need not be a new revision change.
Reference +/- is independent of code edits. JSON retains raw byte/text/position/
region facts plus separate contract classifications and completeness. Shared source
inspection/check/preview outcomes and conservative file-impact facts retain their
existing meanings. Default query sources share one comma-separated line per node;
`--human` lists each occurrence separately, with the same locations and item-level
hints. Duplicate references remain visible in both modes. See [query source contracts](query.md).

These derived readings use the shared bounded cached resolver. They compare selected
versions rather than treating an older anchor's modified outcome as a new change.
They never reanchor or certify that permitted edits still fulfill the intention.

## Both graph hosts

Expanded Implementation forms show source buttons labeled with original anchor
ranges and mode. Clicking resolves against the selected code revision (or working
files) and opens a literal read-only preview with current ranges/outcome. Untrustworthy
mappings show original anchored content explicitly. Historical views allow previews,
not capture. Capture controls append generated metadata to the form; Save/staging
remain normal explicit actions. VS Code applies native document edits rather than
bypassing its dirty buffer; Electron retains managed saves. Source code is inserted
as text, never executable project HTML.

Preview requests use an independent read-only API channel, bound to the published
view and displayed comparison commit. Background synchronization keeps its own work;
a newer click, navigation or revision adoption invalidates obsolete preview replies.
The host coalesces source work to one active request and the newest pending request.

## Limits

- Text is UTF-8/ASCII (UTF-8 BOM accepted); CRLF/LF compare by logical lines. Binary,
  Git symlink/submodule entries, escaped paths and LFS pointers are not line targets.
  Whole-file references still work for binary artifacts.
- Per-file/object: 2 MiB and 10,000 lines. Per request reads: 32 MiB; diff pair:
  20 million line-pair cells. Rename occurrence searches are capped at 128 commits.
  Exceeded budgets are explicit, not truncated successful mappings.
- Batch object reads, caches and no external diff/textconv/lazy-fetch are used for
  source mapping. Query preloads known committed paths/anchors within the call;
  workspace files stay independent of index bytes. Oversized objects consume no
  accepted-content budget and remain separate from eligible bounded objects. Missing objects require an explicit user Git action, not background
  downloads or a silent new source snapshot. There is no persistent source index.

This schema change requires reconstructing **every** maintained Gantt revision/ref,
withdrawn node, actual receipt, ledger, bundle and tracked snapshot. Existing manual
clones remain preserved; create a new external clone with the checkout helper to
use today's corpus. Obsolete self-specification schemas remain intentionally rejected.

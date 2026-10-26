---
id: 7tMgRa8=
type: requirement
parents:
- 0dvOn3A=
---
# Expose everyday commands and focused advanced tools

The everyday vocabulary is init, query, add, update, delete, check and diff.
Query supplies all specification inspection: an unfiltered graph, a selected node
with --max-distance 0, its descendant scope with query ID, and complete ancestor
context with --with-ancestors. Query --with-ancestors
completes the selected bindings with every ancestor, identifying omitted surrounding
children and siblings by ID. Query reads
a complete revision comparison as a tree-shaped view, defaulting to fresh HEAD versus
saved workspace with --base/--target selection. Full target and deleted-base records
carry complete one-line body readings, worded change hints and resolved source context, with forward
references for shared nodes. Query --human retains logical body lines and lists
sources individually; default source items share one comma-separated line. Parent
headers use comma-separated full IDs in both presentations. Query [ID] supports
--min-distance, --max-distance and --influence cutoffs or percentage quotas,
combining criteria by union. --with-ancestors completes that union without consuming
quotas. --max-distance 0 selects only the root before completion. An advanced
--max-bytes bounds the actual encoded response and fails rather than truncating.
Check covers
working files, --staged exact-index files and optional --sources mapping/retention;
--warnings-as-errors remains available. Diff accepts optional positional BASE/TARGET,
defaulting to freshly resolved HEAD versus working files. Root selection stays --root.

Init/add/update accept literal repeatable -m/--message paragraphs and explicit
repeated --parent full IDs where applicable. Bulk file/stdin sources stay
integration-only. Add defaults to requirement and supports --type implementation.
Init and add
create <id>.md paths independently of body text.
Updates replace the supplied parent list; valid manifesto parents stay empty.
Repeatable update --replace OLD NEW selects unique, disjoint original-body passages
as an alternative to complete body input, retaining unrelated binding text.
Delete retains --dry-run and --yes for exact selected-file deletion, retained
reference faults and selected-file warnings. Query --raw reads literal identifiable
or path-selected documents, including malformed text, saved or exact staged bytes
and explicit --target revisions. Query --issues selects faults and potential
descendants; diff --with-context
adds before/current justification and finite cause evidence. --require-valid checks
the complete final candidate, independently of a successful intermediate edit.

add/update/delete may repeat or combine as one bounded invocation, with local
new-node aliases, optional final validity and whole-invocation deletion consent.
Other top-level commands remain standalone. Sources show/capture/
reanchor and recover retain source and transaction recovery controls. Spotlight add/show/flush provides immutable checkout-local spotlights.
Add takes full node IDs and one message with optional --base/--target comparison;
show resolves each record's own context with statuses and advisory workspace drift;
flush requires explicit consent. The application adapter supplies independent
spotlight list/create-from-highlights/reviewed-flush operations. Graph reads expose
sparse workspace state for warning calculation, and Git supplies committed content.
Sources show consolidates resolution and optional literal preview;
capture/reanchor use --dry-run for non-writing previews. Source number, mode,
ranges, explicit revision and staged selection remain meaningful. Raw source JSON,
mixed graph/code revision selection, reviewed deletion plans and cache hints
belong to advanced/integration usage. A hidden api command accepts bounded
structured application read/plan/source requests. Basic help separates the
everyday vocabulary from advanced tooling. Every command and subgroup help explains
its purpose, inputs, defaults, consequences and useful complete examples in detail.

One spelling serves each operation. The current CLI exposes text and --json output;
Git hook/CI setup calls check --staged through owner-controlled Git tooling. Mermaid
export and automatic hook installation are outside the public command surface.

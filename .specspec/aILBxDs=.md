---
id: aILBxDs=
type: requirement
parents:
- 2FfVd-Y=
- 7tMgRa8=
---
# Consolidate parsed and raw inspection under query

Query is the sole top-level specification read command. query ID selects its
descendant scope; --max-distance 0 reads just the selected binding and
--with-ancestors completes justification. Existing comparisons, metrics, issues,
human and JSON presentation retain their contracts.

Query --raw reads a literal canonical document by ID or --path, with --target for
a committed revision and --staged for exact index bytes. --path and --staged bind
raw inspection; reject unrelated comparison/metric/presentation selectors rather
than silently ignoring them. Read invalid documents through the existing safe raw
backend without creating canonical membership. Staged graph validation remains check.

The public top-level vocabulary contains init, query, add, update, delete, check
and diff. Advanced source and spotlight groups retain their domain-specific show
subcommands. Hosts obtain fresh saved mutation context through the existing API-7
read request without base, overlays or retained hints; mutation stdin, consent and
native document persistence retain their owners. Node format and API remain 7.

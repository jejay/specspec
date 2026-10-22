---
id: -fXS-dI=
type: requirement
parents:
- -9Up2uc=
- YkxeXd0=
- 7tMgRa8=
---
# Complete query matches with every ancestor and optional surrounding identities

The query --with-ancestors flag adds every ancestor of every matched record after
normal rooted selection and independent metric unions. Metrics, root-relative
values, population denominators and quotas describe the original matches. Ancestors
are additional complete bindings, deduplicated across all parent paths; they consume
no quota. Root-only selection at --max-distance 0 gives one node's complete upstream
reading. A root without criteria still selects its whole reachable subgraph before
completion. The unfiltered complete comparison already includes every ancestor.
Empty matches acquire no ancestors or surrounding identities.

Complete the same selected-record DAG that query reads: target records/parents for
current nodes and base records/parents for deleted nodes. This supplies every chosen
record's displayed parent path. Historical justification at a particular revision
uses explicit version selection; current readings retain target text for surviving
ancestors even when a deleted record has a changed surviving parent. Original
revision records, old edge deltas and boundary parents remain reconstructible in JSON.

Selection metadata separates matched_ids, additional ancestor_ids and final ids.
Retain original per-criterion priority records and induced final edges. Identify
omitted direct children and siblings of the original matches, where siblings share
at least one direct parent. Their bodies remain outside the reading; each category
and the deduplicated omitted-ID union stay explicit. Added ancestors do not expand
this surrounding-neighbor scope. Compact/human presentation, complete bodies,
source contracts and version choices share the existing query pipeline.

One iterative multi-source parent walk completes all matches before constructing
the final induced view and resolving sources. Deduplicate matched parents before
collecting sibling identities. Reuse the projection, metric batch, revision reads
and source comparison across all criteria and presentations. Selected ancestors
retain their original-graph source badges: including the manifesto can require
source evidence from other branches, even when those bindings remain omitted.

An explicit advanced --max-bytes bounds the actual UTF-8 result plus its final
newline, including terminal escaping or the JSON envelope. Format once and fail
before emitting a partial result when the chosen representation exceeds the budget.
The sole ancestor-reading interface is query; everyday verbs are init, show, query,
add, update, delete, check and diff. Guides, checks and actual retained example
receipts use that current interface. Node format and application API remain 6.

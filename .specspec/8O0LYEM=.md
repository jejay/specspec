---
id: 8O0LYEM=
type: requirement
parents:
- rt-nZHM=
- B71bAFk=
---
# Bound rooted metric walks with inclusive cutoffs and exact population quotas

Use query [NODE_ID] with --min-distance, --max-distance and --influence. An omitted
ID starts at the target manifesto; an explicit full case-sensitive ID can select
a current or deleted record. With no selection arguments the complete comparison
keeps every current and deleted record, including distinct former roots.

Search the selected-record projection, acyclic for valid inputs: current records keep target parents
and deleted records keep base parents. The population is the root and every node
reachable through its full selected edges. Distances count directed edges from
that query root, with zero at the root; influence counts self plus all unique
reachable descendants, independent of which records are subsequently selected.
UI paint continues to use its complete individual revision metrics. Cyclic scopes
use finite shortest/reachability walks; maximum distance is unavailable there.
Cycles outside the rooted population do not invalidate its finite local metrics.
Incomplete parsed scope receives an explicit unavailable-selection diagnostic. Cyclic scopes
use finite shortest/reachability walks; maximum distance is unavailable there.
Cycles outside the rooted population do not invalidate its finite local metrics.
Incomplete parsed scope receives an explicit unavailable-selection diagnostic.

Each absolute nonnegative integer admits distances <= the cutoff or influence >=
the cutoff. Decimal percentages in [0,100] select ceil(population * percent / 100)
nodes; zero selects none and 100 selects the population. Include the root in that
population. Ties use ascending full case-sensitive IDs. Each criterion runs against
the same original population and its own quota; combine only their final ID sets.
A root alone reads its complete reachable subgraph. Graph ordering after selection
retains the existing last-occurrence reading, not metric-priority print order.

Metric selection produces complete matched bindings and external parent links.
Optional ancestor completion adds upstream bindings after the independent quotas. Headers and node metadata preserve all direct parent IDs.
JSON selection metadata identifies root, population, union IDs, induced edges,
boundary parents and each criterion's ordered IDs and values. Scoped base/target
records and change summaries reconstruct the selected part of each revision, with
full parent references; validity describes the independently validated original
snapshots, rather than asserting that a partial view is canonical. The unfiltered
comparison retains its complete API-7 contract. Human changes presentation only.

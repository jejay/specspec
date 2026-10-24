---
id: h3zqGZU=
type: requirement
parents:
- T693TDw=
---
# Read current records with sparse revision hints

Query always compares revisions, using fresh HEAD versus saved workspace by default
and spotlight-style --base/--target selection. Diagnose both graphs and retain explicit
empty/unavailable context. Present complete current and deleted records together
in relationship context, ordered by last occurrence. Full headers retain all parents.

Present all binding content once per selected node: target text for surviving/added nodes
and base text for deleted nodes. The compact default body projection occupies one
line; structured bodies retain their original layout. Current version, extensions
and source locations remain compact metadata above the body. Readable text uses
shared terminal-control escaping.

Show added/modified/deleted for semantic node changes, and
source-changed independently for contract-relevant linked-source changes including
ancestors. File-only identifies literal node-file changes with unchanged
semantic classification. Unchanged
headers have no badge. Display selected revision names once; committed identities
and full before/target records remain available in structured output.

Readable source items retain one location per reference occurrence. Compact output
groups them into one line per node; human output lists them individually. Show the target path and
actual ranges, or the base location for removed declarations. Normal readings are
unmarked. Sparse hints identify ref+/ref- independently of contract-relevant code
changes. Each source class defines permitted edits; those edits add no change cue.
Broken or uncertain links remain explicit, with side labels where needed. Detailed blob,
mode, description, both locations and diagnostics stay in comparison JSON.

Query builds semantic/literal change summaries and complete source facts. Exact
text modifications and canonical patches belong to specspec diff with the matching
revisions. This division keeps query a current-state reading rather than a patch
viewer while preserving reconstructible API-7 comparisons and canonical schema 7.

---
id: cpFRqIM=
type: requirement
parents:
- 0dvOn3A=
- 5d5oDCM=
---
# Use compact reconstructible API 7 data with node format 7

The sole application/structured protocol is API 7; canonical Markdown remains node
format 7 with the same IDs, fields and source grammar. Negotiate/reject protocol
versions explicitly and update host adapters together. Emit one compact UTF-8 JSON
envelope with api_version, ok, result and diagnostics. Keep descriptive field names,
structured diagnostics and explicit successful-plan versus valid-graph meaning.

Return purpose-shaped records: mutation receipts contain changed ID/path and affected
scope, not a whole graph. A comparison carries one complete target, complete previous
records only where a target record differs or is absent, base metadata/resolved commit,
ID-based changes, relationships and source/file impact. Every base node is either
shared with an unchanged target record or present in previous records; added target
IDs are excluded from base reconstruction. Preserve both complete revision structures,
old bodies/sources for deleted/historical nodes, and logical file changes where the
operation requests a full diff. Explicit rooted query selections scope the
comparison records to selected IDs while preserving full parent references and
needed source evidence; selection metadata identifies the partial view and its
external boundary. Ancestor-completed selections distinguish matched IDs, added
ancestor IDs, final IDs and omitted surrounding child/sibling identities. Validation describes the complete original revisions. Reconstruct existing renderer records once in the
shared host adapter; avoid duplicating targets inside an outer loaded snapshot.

HEAD is resolved freshly. Staged deletion leaves HEAD membership and D ghosts intact;
commit removes that membership on reread. Missing comparisons stay explicitly
unavailable. Verified hints remain derived and bounded; no transport payload becomes
canonical tombstones, node fingerprints or write consent. There are no separate slim,
full, UI or LLM JSON dialect switches.

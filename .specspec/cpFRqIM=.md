---
id: cpFRqIM=
type: requirement
parents:
- LvYBN_4=
---
# Use compact reconstructible application protocol data

The shared application protocol is internal; the canonical Markdown node format, IDs, fields and source grammar are independent of it. Negotiate/reject protocol
versions explicitly and update host adapters together. Emit one compact UTF-8 JSON envelope with api_version, ok, result and diagnostics.
Exit code 0 reports a delivered operation or read, 1 a failed check or rejected
request, and 2 an invocation or I/O failure; an edit that leaves the graph invalid
still succeeds. Keep descriptive field names,
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
ancestor IDs, final IDs and omitted surrounding child/sibling identities. Validation describes the complete original revisions. Reconstruct renderer records once in the
shared host adapter; avoid duplicating targets inside an outer loaded snapshot.

HEAD is resolved freshly. Staged deletion leaves HEAD membership and D ghosts intact;
commit removes that membership on reread. Missing comparisons stay explicitly
unavailable. Verified hints are derived and bounded; no transport payload becomes
canonical tombstones, node fingerprints or write consent. One JSON dialect serves every caller.

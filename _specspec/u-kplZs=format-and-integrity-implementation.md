---
id: u-kplZs=
type: implementation
parents:
- tvic3PQ=
- apEb_pM=
sources:
- path: src/specspec/format.py
  symbol: parse_node, serialize
- path: src/specspec/model.py
  symbol: SpecNode.semantic
- path: tests/test_core.py
- path: tests/test_ids.py
  symbol: canonical IDs, current-only validation and collision retry
- path: tests/test_markdown.py
---
## Current deletion-only correction

xu6W0c4=/5d5oDCM= supersede the earlier retired/withdrawal workflow below.
Current schema/API 5 removes the flag and all retire/restore/filter/metadata/badge
paths. Managed delete physically unlinks an explicit batch after DAG checks,
with journal new=null and original-byte/recovery safeguards. Default HEAD-relative
UI ghosts are derived base records, read-only/copyable through staging and gone
after commit; Git HEAD/ref watching refreshes both hosts. Native Delete requires
clean project documents; deleted buffers never resurrect files in overlay reads.
All earlier workflow/schema/test counts below are historical evidence. Gantt's
entire current corpus is rebuilt with 22 physical deletions/reasons in prior Git
commits and a 22-node HEAD, no flagged retained nodes. Earlier root explanations
are in Git, not retained retired files. Source regions/colors/shapes/camera/native
Save remain in scope; the separate current implementation record links actual tests.

## Current compact-ID and history correction

The implementation/verification below records earlier revisions. Its legacy-reader,
schema-migration, original API-2 receipt and root-history compatibility descriptions
are superseded by qowy5AI= and YaXJpGE=. Current production code supports only the
canonical Base64url node scheme, with no old-schema reader or migration command.
The default node-editor association is **/_specspec/???????=*.md. Gantt's maintained
history is rewritten and bundled; tests do not require old root graph revisions.
Earlier run counts are historical evidence, not claims about this revision. The
separate current implementation record documents the new checks and limitations.

# Parse and round-trip hash-free Markdown with readable legacy revisions

format.py validates typed frontmatter and serializes format-three nodes through
ruamel.yaml, preserving unaffected comments and body bytes. model.py contains
plain normalized records, not hash algorithms, stored markers or fingerprints.
There is no status or managed_hash field in current files/JSON. retired is a strict
optional withdrawal boolean; the manifesto declares format_version: 3.

Legacy v1/v2 readers ignore obsolete managed_hash values (including missing/stale
markers), normalize old approval fields away and retain withdrawal. No original
hash verification, provenance rejection, read-time rewrite or hash recomputation
remains. Workspace mutation still validates actual graph/schema consistency;
explicit migrate removes old metadata in one journaled transaction.

Python regressions cover valid manual body/parent/withdrawal edits, strict invalid
metadata, safe paths, UUIDs, optional sources/extensions, CRLF/comments, readable
manually edited legacy Git blobs, marker removal, and stable identities/links/body
bytes during conversion. These are consistency tests, not correctness or review proof.

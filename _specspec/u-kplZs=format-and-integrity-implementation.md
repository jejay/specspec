---
id: u-kplZs=
type: implementation
parents:
- tvic3PQ=
- apEb_pM=
sources:
- path: src/specspec/model.py
  symbol: SpecNode.semantic
- path: src/specspec/format.py
  symbol: parse_node, serialize
- path: tests/test_core.py
- path: tests/test_markdown.py
- path: tests/test_ids.py
  symbol: canonical IDs, current-only validation and collision retry
---
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

---
id: 5ae36d38-63fa-4105-b6df-9da3328b55af
type: implementation
parents:
- 93224022-0c11-4260-b09e-2925b7aacf0f
- ca580dc7-c7fa-48bc-91b1-59243144a0bf
sources:
- path: src/specspec/model.py
  symbol: SpecNode.semantic
- path: src/specspec/format.py
  symbol: parse_node, serialize
- path: tests/test_core.py
- path: tests/test_markdown.py
- path: tests/test_migration.py
  symbol: test_legacy_reader_ignores_hashes_without_exposing_approval
---
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

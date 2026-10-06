---
id: 5ae36d38-63fa-4105-b6df-9da3328b55af
type: implementation
parents:
- 9e4eeace-d288-49bb-8365-6af0372daf5c
- ca580dc7-c7fa-48bc-91b1-59243144a0bf
sources:
- path: src/specspec/format.py
  symbol: parse_node
- path: src/specspec/format.py
  symbol: serialize
- path: src/specspec/model.py
  symbol: SpecNode.digest
- path: src/specspec/workspace.py
  symbol: snapshot_from_files
- path: tests/test_additional.py
- path: tests/test_api.py
- path: tests/test_core.py
- path: tests/test_migration.py
  symbol: test_legacy_reader_checks_original_hashes_without_exposing_approval
- path: tests/fixtures/README.md
  symbol: original v1 fixture provenance
managed_hash: 7b1916c23fbad1515163ac8804d77886352136cce31262d5c48f63125b7b7073
---
# Parse, round-trip, and fingerprint approval-free canonical content

format.py scans strict frontmatter and writes format-two nodes through ruamel.yaml,
retaining unaffected comments and binding body bytes. There is no status field;
retired is an optional strict boolean withdrawal flag. The manifesto carries format
version two. model.py exposes approval-free semantic records and snapshot hashes.

The legacy reader verifies each version-one managed hash with its original status
projection before normalizing accepted/proposed away and mapping retirement to a
boolean. Legacy provenance is private integrity context, not a current JSON status.
snapshot_from_files validates hashes without changing canonical bytes. The writer
rejects raw legacy records rather than generating an invalid mixed-version graph.

Tests include original tool-managed v1 fixtures, malformed metadata, strict boolean
library inputs, UUIDs, source-path safety, CRLF/comments, unmanaged changes, and
identity/body/link/source/extension preservation during conversion. A valid digest
is content integrity, not a confidence score or evidence of review.

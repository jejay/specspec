---
id: 5ae36d38-63fa-4105-b6df-9da3328b55af
type: implementation
status: proposed
parents:
- d51d6da3-4142-4fc7-b593-d935ee5fdf6f
- 9e4eeace-d288-49bb-8365-6af0372daf5c
sources:
- path: src/specspec/format.py
  symbol: parse_node
- path: src/specspec/format.py
  symbol: serialize
- path: src/specspec/model.py
  symbol: SpecNode.digest
- path: src/specspec/workspace.py
  symbol: snapshot_from_files
- path: tests/test_core.py
- path: tests/test_api.py
- path: tests/test_additional.py
managed_hash: 154eeb61e950b4c4b9f18e055ab0f0b8b4367ef5bcf5d064b9996be105b151ee
---
# Parse, round-trip, and fingerprint canonical node content

`format.py` safely scans/parses frontmatter, validates typed fields, and serializes
through ruamel.yaml while retaining unaffected comments and binding body bytes.
`model.py` supplies plain node records and canonical SHA-256 projections;
`snapshot_from_files` checks managed hashes without modifying canonical files.

Verification covers malformed YAML, invalid identities, format versions, unsafe
source paths, comments/CRLF preservation, and unmanaged edits. A valid digest is
content integrity, not evidence of human review.

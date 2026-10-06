# Legacy graph fixtures

`v1/` contains five original tool-managed canonical blobs copied from commit
`817959c`, before removal of the proposed/accepted workflow. They are compatibility
test data, not this repository's active graph. Their original managed hashes are
retained unchanged so tests verify real v1 canonicalization rather than defining
legacy validity solely through newly generated hashes.

The test graph includes accepted and proposed legacy nodes and a retired candidate.
Tests copy it into disposable workspaces, add non-semantic comments/CRLF, verify
original integrity, exercise guarded v2 conversion and recovery, and read both
versions from Git/index snapshots. No fixture mutation edits the live `_specspec`.

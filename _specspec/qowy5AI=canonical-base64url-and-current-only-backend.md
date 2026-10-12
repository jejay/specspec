---
id: qowy5AI=
type: requirement
parents:
- Oou-SvU=
- 6SyZ-BU=
- tvic3PQ=
---
# Generate canonical five-byte IDs and remove superseded readers

Use secrets.token_bytes(5) and padded RFC 4648 Base64url. The complete eight-byte
ASCII string ends in one equals sign; seven payload symbols have 40 bits, not 42.
The final symbol must have zero pad bits. Node paths are _specspec/<id><slug>.md:
the equals sign is both part of the ID and the sole separator before the summary.
Full IDs remain case-sensitive in references, messages, API and UI.

Generate under the managed writer lock, reserving every current node's ID,
including withdrawn ones. Retry exact and ASCII-casefold collisions, regardless
of summary, for Windows/portable filename safety. Reject case-only node aliases
in input graphs too. Cryptographic randomness is for unbiased identifier generation,
not a secret/authentication claim; local checking does not prevent branch merge
collisions. Init has no graph to collide with.

Keep the current format/API 4 shape, without node fingerprints or managed hashes; validate only that current schema
and these IDs. Remove v1/v2 normalization, obsolete hash/status recognition, the
migrate command and host migration controls. Old UUID/old-version snapshots fail
with diagnostics, without silent conversion or pretending to be a valid baseline.
Keep manual-edit/schema/DAG/byte-transaction/recovery protections. Mermaid export
uses an injective ASCII-safe ID representation. VS Code associates only the new
equals-delimited filenames; the Python backend still verifies the actual node.

Convert the two working graphs once through a temporary tool-managed migration
with a saved mapping, original bytes, validation and recovery journal. That
conversion utility is not a permanent production compatibility feature. Update
current documentation/links/references. Keep prior reasoning as withdrawn/history
text where useful; do not mistake such prose for supported old runtime schemas.
Persisted host drafts/cameras are not silently rekeyed or claimed compatible.

Origin: a separate implementation choice following the user's resolved encoding
and compatibility intentions. It supersedes the previous analysis's suggestion
to retain legacy readers and the earlier schema migration contract.

## Source-region refinement

jsIUeP0=/VnSF9BE= choose structured blob-addressed strict/expanding ranges and
current-only format/API 4. Five-byte node IDs and manual-edit/writer protections
remain. Source blob IDs identify immutable Git content, not node-integrity gates.
All maintained Gantt history is reconstructed under current tools; API 3 is now
obsolete. The earlier compact-ID conversion and its actual checks remain history.

---
id: d3bf2d3c-0172-4f67-807c-a73047018d83
type: requirement
parents:
- 7c9750b8-c8da-46a6-9248-c409da45cf19
- 955b905a-6220-4d5c-b0ca-fab86b6b6db8
- 624d0f3c-391d-4575-be87-3001f16052f6
- af518184-9eb4-4612-bfda-2876b4dbeb6a
---
# Make the compact-ID encoding conflict explicit before implementation

RFC 4648 sections 3.5 and 4 require zero pad bits for canonical encodings. Seven
Base64 symbols followed by one equals sign encode exactly five octets: 40 random
bits, with only four significant bits in the seventh symbol. Seven independent
six-bit symbols would carry 42 bits, but appending an equals sign then produces
noncanonical encodings for three quarters of the possible final symbols. A
permissive decoder accepting them does not make the encoder standards-compliant.

The standard Base64 alphabet includes slash, which cannot be part of a direct
node filename. RFC 4648 section 5 defines the distinct Base64url alphabet, replacing
plus/slash with hyphen/underscore, while retaining the same padding rules.

Reference: https://www.rfc-editor.org/rfc/rfc4648.txt (sections 3.5, 4, 5).

## Alternatives and unresolved scope

Recommend canonical padded Base64url over five cryptographically random bytes:
eight characters including the final equals sign, 40 bits of initial entropy,
and filenames such as Zm9vYmE=summary.md. This recommendation is not yet the
implemented encoding and does not rewrite the user's request. Alternatively,
seven uniformly random Base64url symbols plus a literal equals-sign terminator
can retain 42 bits, but must be documented as a custom ID scheme, not canonical
padded Base64. Ask which constraint matters before choosing between these.

Clarify whether existing working UUID nodes should be converted or only new nodes
receive compact IDs. Keeping existing IDs avoids breaking external references.
Rekeying existing nodes would require an explicit whole-graph operation updating
IDs, filenames and parents, with an old/new mapping and review of documentation
links and persisted editor state. Historical Git bytes must stay unchanged.
Do not repurpose the existing schema migration, which currently preserves IDs,
without separately documenting that changed contract. Version/compatibility policy
also remains a choice rather than an inevitable schema bump.

## Implementation consequences identified by inspection

Generate/retry inside the existing managed writer lock against the entire current
project graph, including withdrawn nodes, regardless of filename summary. Init
has no existing graph. Independent nested workspaces have independent ID spaces.
Reject or regenerate case-only aliases as necessary for portable filename safety
on Windows/case-insensitive filesystems; canonical case-sensitive IDs alone do not
address that problem. These IDs are references, not credentials. Local collision
checks cannot guarantee uniqueness across independent branches before a merge.

Validation must recognize the chosen full ID in both id and parents and enforce
its matching equals-delimited filename. Preserve readable UUID snapshots and
legacy schema behavior deliberately. Ordinary update/retire/restore should retain
identity. The current writer generates before acquiring the mutation lock and has
no retry loop, so merely swapping uuid.uuid4 is insufficient.

Audit Mermaid identifiers: the current exporter only replaces hyphens, so equals
signs and underscores need an injective diagram-safe representation. Update VS
Code's *--*.md editor association for the new filenames while retaining legacy
files. Python remains the schema authority; shared and Electron hosts currently
pass full string IDs rather than generating IDs themselves.

Verification should include deterministic byte/encoding vectors, forbidden/nonzero
pad bits where applicable, collision retry against live/retired nodes and different
summaries, lock timing, case-only aliases, filenames, full-ID CLI/context/exports,
unsaved document overlays, legacy/staged/revision snapshots and interrupted edits.
No production code, node identities or historical files changed in this analysis.

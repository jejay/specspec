---
id: qowy5AI=
type: requirement
parents:
- F5JaC_4=
- ME4UXTA=
- pA2ls_g=
---
# Define canonical five-byte IDs and the current typed node schema

Encode `secrets.token_bytes(5)` with padded RFC 4648 Base64url: seven payload
symbols plus `=`, 40 random bits and canonical zero pad bits. Paths are
`_specspec/<id>.md`. References are full and case-sensitive. Generate
inside the writer lock and retry exact or ASCII-casefold collisions against every
current node. Validate casefold aliases for portable
filename safety. Random IDs are project references; branch-merge collision checking
remains part of graph validation.

Current node format 7 fields are: required `id`, `type`, unique `parents`; manifesto
integer `format_version: 7`; optional implementation `sources`; optional namespaced
JSON-compatible `extensions`. Types are manifesto, requirement and implementation.
Requirement parents are manifesto/requirement; implementation parents are requirements.
Read the unique manifesto/version before full parsing. Unsupported versions,
unknown fields, duplicate YAML keys, tags/aliases, coerced types, unsafe filenames,
invalid UTF-8 and files exceeding 1 MiB produce explicit diagnostics. Direct regular
node files are the canonical entries. Source-region syntax is specified separately.

Preserve unaffected frontmatter comments and body bytes on targeted writes.
Normalize tool-controlled fields when writing them. CLI arguments and hosts retain full IDs, including
hyphen-leading identities; VS Code associates `**/_specspec/???????=.md` and verifies
the actual resource through the backend.

---
id: EKAJyVM=
type: requirement
parents:
- _wJJQko=
- _yahyM4=
- DiIJxaQ=
- W8_8BXA=
- 9ja11UM=
retired: true
---
# Use UUID identities and strict version-one frontmatter

Use lowercase UUIDv4 identifiers and `<id>--<slug>.md` filenames. Store incoming
relationships in `parents`, and put `format_version: 1` on the manifesto. Reject
unknown fields, duplicate keys, explicit YAML tags/aliases, malformed identities,
invalid node relationships, and unsupported format versions before editing.

Permit headings and lists as ordinary Markdown. Split content when independent
review or reuse warrants another ID, rather than assigning list items automatic
node semantics.

Origin: [CONCLUSION_SPEC.md](../CONCLUSION_SPEC.md), files and schema.

## Withdrawal

The version-two schema removes approval status while retaining strict managed graph metadata and readable version-one history.
History is retained; see the risk-proportionate-review intention and its separate schema conclusion.

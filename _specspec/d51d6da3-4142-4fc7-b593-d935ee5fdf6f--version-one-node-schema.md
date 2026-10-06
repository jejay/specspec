---
id: d51d6da3-4142-4fc7-b593-d935ee5fdf6f
type: requirement
status: proposed
parents:
- 955b905a-6220-4d5c-b0ca-fab86b6b6db8
- 95287a17-697f-43ad-80b0-140d5e0ec058
- 4d1f2eee-8125-4e3f-b9b4-649517875d87
- 48f77f19-391f-46d0-b06f-ec7530be4575
- 5b93cd32-168c-488f-b4f9-caf03fe2652d
managed_hash: d2ecfbc283a48d8c0690d2d726d37d569a7c95e8e767e76bfb42188a82525e1b
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

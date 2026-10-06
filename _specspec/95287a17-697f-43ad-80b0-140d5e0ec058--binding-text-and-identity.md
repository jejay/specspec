---
id: 95287a17-697f-43ad-80b0-140d5e0ec058
type: requirement
status: accepted
parents:
- 955b905a-6220-4d5c-b0ca-fab86b6b6db8
managed_hash: c872387f5933b555fd15d99c7e6f7274b6c28ae9c6fd891183539fe85d944e18
---
# Separate stable references from discovery summaries

Reference nodes by identifier, not by their non-binding English filename summary.
Frontmatter records the node type and dependency identifiers; the Markdown body
contains the binding specification text. Filename summaries aid discovery without
becoming requirements themselves.

Origin: [INTENTION_SPEC.md](../INTENTION_SPEC.md), managed directory section.

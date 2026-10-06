---
id: 955b905a-6220-4d5c-b0ca-fab86b6b6db8
type: requirement
parents:
- b8983d8c-3dc0-4588-b74f-17721bfc4f5c
managed_hash: c6594d49baa2bbce8938ee8d87141d476976db043e17e89f51d80bed01d46f62
---
# Keep canonical nodes directly in the project-root directory

The project-root `_specspec` directory directly contains node Markdown files and
nothing else. Each file represents one node, with YAML frontmatter and binding
Markdown text. The manifesto may hold global metadata such as a spec format
version; no separate configuration file belongs inside the canonical directory.

Origin: [INTENTION_SPEC.md](../INTENTION_SPEC.md), managed directory section.

---
id: _wJJQko=
type: requirement
parents:
- XV5_rPQ=
---
# Keep canonical nodes directly in the project-root directory

The project-root `_specspec` directory directly contains node Markdown files and
nothing else. Each file represents one node, with YAML frontmatter and binding
Markdown text. The manifesto may hold global metadata such as a spec format
version; no separate configuration file belongs inside the canonical directory.

Origin: [INTENTION_SPEC.md](../INTENTION_SPEC.md), managed directory section.

---
id: _wJJQko=
type: requirement
parents:
- XV5_rPQ=
---
# Keep canonical nodes in a flat project-root directory

The project-root `_specspec` directory directly contains one Markdown file per node.
Each file has YAML frontmatter and binding Markdown text. The unique manifesto
contains global `format_version` metadata. Runtime state belongs in the separate
ignored project-root `.specspec-local` directory. Discovery selects the nearest
containing `_specspec`, including a nearer directory with invalid contents.

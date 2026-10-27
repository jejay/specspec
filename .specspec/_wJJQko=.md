---
id: _wJJQko=
type: requirement
parents:
- XV5_rPQ=
---
# Keep canonical nodes and local runtime data together

The project-root `.specspec` directory directly contains one Markdown file per node.
Each file has YAML frontmatter and binding Markdown text. The unique manifesto
carries internal schema metadata. The reserved ignored `.specspec/local/` subtree
holds checkout-local locks, journals, spotlights, caches and diagnostic work. It is
not canonical membership, including during revision or exact-index inspection.
Discovery selects the nearest containing `.specspec`, including an invalid entry.

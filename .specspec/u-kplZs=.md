---
id: u-kplZs=
type: implementation
parents:
- qowy5AI=
- MmfPuhY=
- Pek6TGE=
sources:
- path: src/specspec/format.py
- path: src/specspec/model.py
- path: tests/test_core.py
- path: tests/test_ids.py
- path: tests/test_markdown.py
---
# Parse node files of the current format and rewrite only what an edit changes

`format.py` reads frontmatter with ruamel.yaml, so that the manifesto and its format version are known before a node is parsed in full. It validates the typed fields and serializes nodes of the current format. `SpecNode` in `model.py` gives the normalized record of a node, with the body in LF and the parents and sources sorted, and nodes are compared by that record. A write keeps the logical text of the body where the edit leaves it alone, the frontmatter comments and extensions, and the references as they stand. It keeps the newline style of the document and appends a final newline only when the complete document lacks one. Raw reads and the byte checks of the writer use exact bytes. Diagnostics name an unsupported version, an unknown field, a YAML value of another type than its field, an unsafe path, a YAML alias, a duplicate key, invalid UTF-8, more than 256 sources on one node and a file larger than 1 MiB.

Frontmatter that cannot be loaded gives a `FORMAT` diagnostic for its own file while the other nodes still load: nesting deeper than the parser's stack, an integer beyond Python's digit limit or an impossible date. An integer too large for JSON gives `SCHEMA`. A frontmatter delimiter is a whole line that ends in LF, CRLF or CR. `tests/test_core.py`, `tests/test_ids.py` and `tests/test_markdown.py` exercise Markdown of the current format, comments, CRLF and Unicode text, optional structured sources and extensions, valid edits made by hand and the diagnostics of rejected input.

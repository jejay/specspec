---
id: u-kplZs=
type: implementation
parents:
- qowy5AI=
sources:
- path: src/specspec/format.py
- path: src/specspec/model.py
- path: tests/test_core.py
- path: tests/test_ids.py
- path: tests/test_markdown.py
---
# Parse and target-write the current Markdown schema

`format.py` uses ruamel.yaml to bootstrap manifesto/version, validate typed
frontmatter and serialize format 5 nodes. `SpecNode` supplies normalized records
and semantic comparison. Metadata updates preserve unaffected body bytes; body
updates preserve frontmatter comments/extensions and stable references. Diagnostics
identify unsupported/unknown/coerced YAML data, unsafe paths, aliases/duplicate keys,
invalid UTF-8 and entry/file budgets.

Tests exercise current-schema Markdown, comments, CRLF/Unicode, optional structured
sources/extensions, valid manual edits and explicit rejection diagnostics.

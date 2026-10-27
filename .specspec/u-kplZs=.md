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
frontmatter and serialize current-schema nodes. `SpecNode` supplies normalized records
and semantic comparison. Writes preserve unaffected logical body text, frontmatter comments/extensions
and stable references while retaining local newline style and appending only a
missing complete-document terminator. Raw reads and physical guards stay exact. Diagnostics
identify unsupported/unknown/coerced YAML data, unsafe paths, aliases/duplicate keys,
invalid UTF-8 and entry/file budgets.

Tests exercise current-schema Markdown, comments, CRLF/Unicode, optional structured
sources/extensions, valid manual edits and explicit rejection diagnostics.

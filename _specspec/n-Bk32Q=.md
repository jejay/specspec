---
id: n-Bk32Q=
type: implementation
parents:
- rQTg56g=
- RY5LFw8=
sources:
- path: docs/spotlights.md
- path: docs/cli.md
- path: src/specspec/annotation_commands.py
- path: src/specspec/annotations.py
- path: src/specspec/application.py
- path: src/specspec/cli.py
- path: src/specspec/editor.py
- path: tests/test_annotations.py
- path: tests/test_cli_compact.py
- path: tests/test_spotlight_backchannel.py
---
# Implement metadata-only comparison spotlights and sparse drift warnings

The Python backend publishes bounded immutable local-format-2 message/ID/comparison
records under the shared workspace lock. Explicit refs pin commits, the default
workspace/HEAD context stays live, and sparse workspace summaries checksum only
uncommitted added/modified nodes with null deletion markers. No node copies or
retained-text preview are part of capture. Git exclusion, tracked-state refusal,
protected malformed metadata, limits and reviewed flush retain their boundaries.

CLI add/show/flush uses color-free ID/message arguments and --base/--target.
Show derives statuses and titles from each record's comparison and reports drift
without rejecting available ID matches. Application reads expose sparse workspace
state for shared UI warnings. UI creation uses trusted native overlays without
saving documents or managed drafts. Explicit flush also cleans obsolete local
blob files; unsupported previous metadata gets an actionable diagnostic.

Backend and current-schema Gantt regressions cover explicit commit/branch contexts,
added/deleted/unchanged selection, literal dirty-only checksums, native overlays,
HEAD movement and drift, absence/unavailable refs, atomic rejection/publication,
immutable messages, local exclusion, bounded metadata and reviewed flush races.

---
id: rQTg56g=
type: requirement
parents:
- 7tMgRa8=
- P2i_png=
---
# Parse spotlight IDs and one message with base and target options

Expose spotlight add NODE_ID... MESSAGE with --base REV and --target REV|workspace.
The implicit comparison is live HEAD versus workspace; explicit Git refs resolve
to immutable commits. Read the leading canonical full IDs, including dash-leading
IDs, then join the remaining message words. Require unique IDs, at least one member
and a nonblank message of at most 500 characters. Colors are ordinary message text,
not structural arguments. Validate identities from parsed target/base records, declared missing references
and inventoried canonical filenames before publication. Unreadable file identities
remain unavailable bindings rather than invented graph membership. No input JSON/file is needed.

Spotlight show optionally selects one full shot ID and reports each record's own
comparison, message, derived comparison/availability status, title and workspace/context warnings.
--json exposes the same records and structured statuses. Explicit spotlight flush
--yes clears the local store. The color-free application creation operation accepts
one message and node-ID list, with trusted current comparison and native overlays.

---
id: c2WCD6c=
type: requirement
parents:
- TaNM294=
- P2i_png=
---
# Store sparse workspace drift summaries beside comparison references

Use one metadata-only immutable record containing one message, ordered unique full
node IDs and a base/target comparison. Explicit Git refs resolve to full immutable
commit IDs at capture. The implicit default stores HEAD versus workspace, following
fresh HEAD on display. Workspace targets also store their capture HEAD and a sparse
map of all uncommitted node changes: literal UTF-8 SHA-256 checksums for added or
modified nodes and null markers for deletions. Git identifies dirty saved files and trusted native overlays contribute unsaved
changes. Clean committed nodes use their commit context. This captures drift without copying canonical node text.

Compare the live workspace summary with the captured one when displaying a record.
Warn separately about HEAD movement, changed workspace nodes and unavailable
context. Treat these as advisory: highlight any selected IDs in the displayed
target or deleted base, report missing IDs and derive A/M/D/unchanged from that
comparison. Native overlays participate in UI capture and warning calculation;
managed form drafts retain their separate save owner. Checksums are local drift
hints, independent of canonical node schema and mutation protection.

Local spotlight format 2 has one metadata file per shot, bounded count and metadata
size, protected malformed records, atomic publication and reviewed explicit flush.
Older local records remain untouched with an actionable flush diagnostic. Explicit
flush also clears obsolete retained blob files. The current canonical schema and
maintained example history remain unchanged.

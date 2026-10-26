---
id: 7kYVG_E=
type: requirement
parents:
- 0dvOn3A=
- Yfy0414=
---
# Present complete node-aware review diffs

Default diff output is a full review diff, preceded by a concise summary. Group by
stable full node ID, type, readable heading and old/new paths. Show all changed binding
text hunks with context; show added/deleted records completely. Expose exact parent,
type, source-reference and extension changes and an intelligible added/
removed relationship overview labelled with IDs and revision-appropriate headings.

Represent every canonical file change, including frontmatter comments, whitespace,
line-ending and final-newline-only edits. Literal unified canonical-file patches may
accompany the semantic node presentation so normalization never hides a change. These
are review records; ordinary Git supplies directly applicable byte patches. A summary
alone is explicitly requested, not substituted for the full default. Invalid or
unavailable revisions carry actionable diagnostics and incomplete impact, never a
fabricated empty comparison.

Separate linked-source file changes and conservative potential impact from direct
specification modifications. Report their paths and linked implementations without
dumping unrelated implementation-code patches or claiming that every affected node
is invalid. Snapshot reads leave checkout, index, refs and source files unchanged.

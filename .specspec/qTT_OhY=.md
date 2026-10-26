---
id: qTT_OhY=
type: requirement
parents:
- w7A25ZA=
---
# Normalize logical node newlines while respecting document storage

Represent logical UTF-8 node text with LF: CRLF and bare CR encode the same line
boundaries. Compare node records, canonical-text changes, patch text, query hints
and mutation outcomes using this representation. Preserve other characters,
indentation, trailing spaces, blank-line counts and final-newline presence.
Unreadable binary material retains explicit literal/unavailable evidence.

Managed updates and native edit plans use the opening frontmatter delimiter's
newline style for the target document. New nodes use LF. Body messages, bulk input
and replacement NEW keep their literal content with newline encoding adapted to
that storage style. Preserve unmatched content and metadata; source-mapped OLD
matching and bounds retain their existing owners. Size checks assess actual
serialized target-style bytes, separately from original argument/input budgets.

Ordinary diff includes all meaningful canonical text and metadata changes with
LF patch lines. Encoding-only differences contribute no node or file-only change
and no newline-counter dump. EOF termination changes use ordinary patch markers.
Structured file-patch records retain existing physical-layout metadata where a
meaningful change exists. Raw query remains exact physical evidence.

Reads and comparisons leave files unchanged. Git configuration, attributes, index,
hooks and filters remain owner-controlled; application normalization needs no
repository setup or filter execution. Native Save/undo remains VS Code-owned.
Original-byte checks, journals, recovery, immutable Git blobs and cache verification
remain byte-exact. Current node fields, accepted encodings and API-7 field grammar
retain their existing schema; maintained LF examples keep their actual receipts.

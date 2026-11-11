---
id: jWl96h0=
type: requirement
parents:
- h3zqGZU=
- VnSF9BE=
---
# Compare source declarations and resolved version locations independently

For each node, compare the exact multiset of source records in normalized ordering.
Equal records pair by occurrence; unequal records are explicit removals/additions.
Keep every reference and duplicate, with source numbers into each side's normalized
record. A reference's declaration membership is independent of its code comparison:
resolve each distinct union reference against both code versions even when only one
node version declares it. Changes of anchors/ranges/descriptions remain declaration
changes rather than inferred code changes.

Use shared SourceReader strict/expanding mapping, rename/context evidence, safe
paths, batched objects, caches and budgets. Structured readings retain each side's
actual path, inclusive ranges and outcome. Readable items show one location
with sparse change/uncertainty hints; grouping is a presentation choice. Whole text-file hints resolve to all logical lines;
empty text files have an empty selection. Missing/ambiguous/conflicting/unavailable
mappings retain their outcomes; partial strict fragments remain untrusted selections.
Binary, LFS, invalid UTF-8 and budget-limited files retain explicit line uncertainty.

Compare cached file bytes separately from selected logical text and path/range
coordinates. Equal selected text at equal coordinates is same; equal text at changed
coordinates is relocated; unequal trusted selected text is modified. Untrusted or
unreadable selections are unavailable. These facts compare the selected revisions,
independently of whether either resolver reports changes from an older anchor.
Known binary/pointer bytes can still compare while line information is unavailable.

Keep the shared conservative declared-file impact and ancestor propagation separate
from these finer facts. Raw changed-file evidence remains available for conservative
review; query change hints are separately interpreted through each reference's
strict/expanding/path-only contract. Permitted edits add no source-change cue. Resolve committed sources at
pinned commits and workspace sources from saved files, reading each path once per
side where available. Live file reads are not an atomic cross-file snapshot. Reads
never reanchor, write objects/refs, fetch, stage, commit or approve implementation.

---
id: VnSF9BE=
type: requirement
parents:
- jsIUeP0=
---
# Track a source region strictly or let it expand, and report every uncertain mapping

A source of an implementation is either `{path, symbol?}` or `{path, symbol?, blob, mode, ranges}`, in which `blob`, `mode` and `ranges` appear together. Accepted are a full Git blob ID of 40 or 64 lowercase hexadecimal digits, the mode `strict` or `expanding`, ranges as sorted `[start, end]` pairs that are positive, inclusive and free of overlap, and a path in canonical POSIX form relative to the project. A path that leaves the project, a malformed range, an entry or a path of an unsafe type and an unsupported value are rejected with a diagnostic.

A strict link moves with the original lines that survive and reports a conflict for an insertion inside its region and for any replacement or deletion that touches it. An expanding link takes in insertions inside its region and replacements that lie wholly within it, and reports the modification as information. Both leave out insertions at the outer edge of a region and the gaps between separate regions. A deletion, an ambiguous copy or move, a change across the edge of a region and a missing object are each reported as what they are.

A link is resolved against the text of the working tree, the exact bytes of the index or the files of a commit, with the metadata of the node taken from the selected revision. A preview is literal and read-only and names the kind of target, the mapped ranges, the mode and the outcome, and it shows the originally anchored content when the mapping is unreliable. An object of the wrong type, a symlink or submodule entry, binary or LFS data, invalid UTF-8 and an exceeded limit each show as an uncertain result. Git reads, diffs and mappings are batched, cached and limited in size, and external diff tools, textconv filters and lazy fetching are switched off.

A capture reads HEAD by default and accepts `--staged`, a repeated `--range START:END`, a mode and a symbol, and its preview writes nothing. Capture and reanchor write the node through the ordinary writer. Reanchor uses the mapped ranges when they are reliable, or the replacement ranges that are given explicitly for a conflict. `check --staged --sources` evaluates the exact staged graph and code and the retention of the anchored blobs, and a staged check without `--sources` evaluates the structure of the graph. Navigation to a region gives context, and a change anywhere in a linked file counts as possible impact.

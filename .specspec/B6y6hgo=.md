---
id: B6y6hgo=
type: requirement
parents:
- AY1g-sU=
- jWl96h0=
- nLqvWcM=
---
# Offer compact and human query presentations with comma-separated lists

The default readable `query` prints each body on one line and groups the source items of a node on one line that begins with `sources: `, separated by a comma and one space. The items stand in the normalized order of the comparison, and every duplicate occurrence appears. Each item has its selected path and ranges and its own hints: a link that was added or removed, a broken link, a restored link or an uncertainty. A path with unusual characters, a comma among them, is quoted in the same way as on a source line of its own. A range is written as `12-30` or as a single line number, and several ranges of one item are joined by commas.

With `--human` each body keeps its logical lines, blank lines, indentation, tabs and trailing spaces. The newline encodings of the node are normalized for reading, and the text passes through the shared escaping of terminal control characters. Each source occurrence has a `sources: ` line of its own. In both presentations a current node shows its target body and a deleted node its base body, and both have the same full lowercase headers, the same sparse hints, the same alignment of the root, the same compact rails and the same place of a record at its last occurrence.

In both presentations a full header names every parent after `@`, in ascending order of the full IDs compared case-sensitively, separated by a comma and one space, the parent under which the record is printed included. The same punctuation in every list makes a reading quick to scan, and complete items give a reviewer the context. `--human` chooses a presentation of text. `--json` gives the complete comparison of the application protocol, which is the authoritative form, also when it is combined with `--human`. Both presentations come from the same fresh read and the same source facts, within the same limits, and both are read-only.

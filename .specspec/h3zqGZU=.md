---
id: h3zqGZU=
type: requirement
parents:
- kiOMI7I=
---
# Show the current nodes of a comparison with sparse hints of what changed

A parsed `query` compares two revisions: by default a freshly resolved HEAD with the saved working files, and with `--base` and `--target` the revisions that are named, in the way a spotlight selects them. It diagnoses both graphs and states explicitly what of the comparison is empty or unavailable. Current and deleted nodes appear together with their complete records, each among its relationships, and a full header names all parents.

All the text of each selected node appears once: the target text of a node that survives or was added, and the base text of a node that was deleted. By default a body takes one line. A structured record keeps the logical layout of the body, with CRLF turned into LF. Extensions and source locations are compact metadata lines above the body, and an ordinary header carries no internal format version. Readable text passes through the shared escaping of terminal control characters.

A header carries a hint where something changed. `added`, `modified` and `deleted` mark a change of the node record. `source-changed` marks, independently of these, a node whose linked code changed in a way that matters for the mode of the link, and every ancestor of such a node. `file-only` marks a node file that changed literally while the node record is the same. The header of an unchanged node has no hint. The names of the compared revisions appear once, and the structured output holds the commit IDs and the full records of the base and of the target.

A readable source item gives one location for each occurrence of a link. The compact output puts the items of a node on one line, and the human output lists them one by one. An item shows the path in the target and the actual ranges, or the location in the base for a link that was removed. A normal reading is unmarked. `ref+` and `ref-` mark a link that was added or removed, independently of a relevant change of the linked code. Each mode of a link defines the edits that it permits, and a permitted edit adds no hint. A broken or uncertain link is named as such, with the side it concerns where that is needed. The blob, the mode, the description, both locations and the diagnostics are in the JSON of the comparison.

`query` builds summaries of the changes to nodes and of the literal changes to node files, and the complete facts about sources. The exact changes of text and the patches of node files are shown by `specspec diff` for the same revisions. `query` is thus a reading of the current state, and both revisions can be reconstructed from its comparison in the application protocol.

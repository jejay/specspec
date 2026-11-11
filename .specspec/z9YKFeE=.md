---
id: z9YKFeE=
type: requirement
parents:
- jWl96h0=
---
# Mark a change of linked code in query only where the mode of the link forbids it

`query` reads a change of linked code by the mode of the link as it was declared. A strict link accepts a region that moved and can be followed reliably, edits at its outer boundary, in the gaps between its regions and outside them, and line ends that are logically equal, as long as the selected content is protected. An expanding link accepts in addition the edits inside its region and contained in it that the shared resolver maps reliably, a partial deletion that leaves a selection among them. A link to a path alone, the whole file, requires a safe regular file and neither stable contents nor readable lines: a binary file, an LFS pointer or a large file causes no warning about lines.

A permitted change leaves the readable source row and the `source-changed` hint of the node unmarked. A link that was added to or removed from the metadata shows `ref+` or `ref-` independently. The exact results for bytes, for text, for position and in relation to the anchor are raw facts of the comparison in JSON, next to a separate classification of the link: `same`, `changed` or `unavailable`. The inspection of sources, their preview, their check and the cautious impact of a changed file, which the tools share, each have a meaning of their own. `query` derives its `source-changed` hint from the classification of the link and never from the raw impact of a file.

Two readings that are both reliably valid mean that nothing relevant to the link changed. A known change between valid and broken is a change, and that includes the restoration of a broken link. A link that is missing on both sides, or broken in the same way on both, shows no new change, and its existing problem stays visible. Ambiguous or unavailable evidence is reported as such and never becomes an invented change or an invented unchanged result. Identical file bytes with identical facts of resolution establish that the revisions do not differ, while a problem of the mapping that existed before stays visible. Every link of either revision is compared, whichever revision of the node declares it.

The `source-changed` hint marks the nodes with a known change of this kind and their ancestors in both original graphs. A comparison that could not be decided has explicit hints on its source rows and a completeness flag in the structured output, so that no verdict claims a certainty that is missing. The affected scope of a query includes these effects, and the raw facts about the impact of changed files stay available under names of their own for a wider review. Reads use the same shared resolver with its limits and caches. They change neither anchors nor metadata, fetch and stage nothing, and leave the judgment of an implementation to the reviewer.

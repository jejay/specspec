---
id: 6p7T7CY=
type: requirement
parents:
- sJ5dyh4=
---
# Report what an edit did as full node IDs grouped by action

The readable receipt of an edit names nodes by their full IDs. Each action with at least one node has one line that starts at the left margin: the action, a colon and one space, then the IDs separated by a comma and one space. The actions are `Added`, `Modified`, `Deleted` and `Unchanged`, in this order, and within a line the IDs keep the order of the targets of the writer. The manifesto that `init` creates is listed under `Added`. A full ID appears once in the line of its action. The receipt speaks of nodes, and the paths of their files are found in the structured records, in raw reads, in diagnostics about files and in the patches of a full review.

The action of a node follows from its logical text before and after the invocation, which the writer compares under its lock. A document that is new is `Added`, a document whose logical content differs is `Modified`, a selected document that is removed is `Deleted`, and a document with equal logical text is `Unchanged`. A difference in newline encoding alone is `Unchanged`, while the checks of the transaction compare exact bytes all the same. Edits of the body, of the parents and of the sources are classified in this one way, replacements and combined commands included. The receipt describes this one invocation, and a comparison with Git describes the revisions that are selected for it.

A preview that writes nothing uses `Would add`, `Would modify` and `Would delete` for the same changes and `Unchanged` for equal logical text. An ID that a preview generates is provisional and reserves nothing. The receipt of a completed edit is printed after the transaction has verified its result, and a rejected operation prints its diagnostics. Each of these is reported on its own, apart from the action lines: the validity of the saved or of the proposed graph, an incomplete analysis, the possibly affected scope, what `init` did with the agent instructions and the consent to a deletion.

The local names that an invocation gave to new nodes are reported on one `Aliases` line, as pairs separated by a comma and one space, without padding into columns. This line maps local names to IDs and is no further action line. Lines about structure and diagnostics name the IDs that they are about. A structured receipt of the application protocol carries its fields with the IDs and the paths. The classification by action is a transient part of the result of one invocation inside the Python backend, and a node file has the same fields whatever happened to it.

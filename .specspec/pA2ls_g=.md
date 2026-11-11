---
id: pA2ls_g=
type: requirement
parents:
- uAjln2M=
---
# Check shortcut freedom in one shared validator of the current node format

The current node format requires a rooted acyclic graph of intentions and conclusions whose direct links are free of shortcuts, that is, transitively reduced. The application protocol reports the success of an operation and the validity of the graph separately. A reader handles the current format alone and reports a graph of another format version with an explicit diagnostic. Every revision of the maintained Gantt history and every recorded receipt uses this format, and a rebuild of that history leaves clones made by hand with their experiments as they are.

One graph validator in the backend, shared by all tools, checks the whole graph for shortcuts once the parent references, the parent types and the absence of cycles are sound. Each redundant parent produces a `REDUNDANT_PARENT` diagnostic with the affected node, the direct edge and an alternative path, which is the same on every run. An edit through the writer reports the diagnostics of the saved graph and of the complete candidate graph, and `--require-valid` requires the whole candidate to pass before anything is written. An edit whose result is an invalid graph on the way to a valid one is written with explicit diagnostics and with the same safeguards of the write transaction. The same rule applies to reads of the working files, of the exact index, of a revision and of unsaved editor text laid over the files. Hooks and CI that an owner has set up call `check --staged`, which reads the actual bytes of the index. Invalid text in an editor's own document can be diagnosed and repaired.

A change to the parents of one node can make a link of another node redundant. The diagnostics name every affected edge. The related changes are made deliberately, and an edit that the writer rejects leaves the files as they were. An owner can prepare a coherent change in the Markdown files, or combine ordinary `add`, `update` and `delete` steps in one explicit invocation that is recovered as a whole. Each `update` step names one node, and the optional validity check judges the complete final candidate. Inspection, the planning of a candidate and recovery work on an invalid graph as well. Validation reports and leaves every relationship exactly as it is written. Validity follows from the files alone, and the commands work on the current node format alone.

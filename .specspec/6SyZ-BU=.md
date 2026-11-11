---
id: 6SyZ-BU=
type: requirement
parents:
- ME4UXTA=
---
# Write every edit as a locked and journaled transaction, on a valid or an invalid graph

An edit through the tools is explicit: the writer changes exactly the nodes that the edit names. Under a lock on the project, the writer takes stock of the node files that are actually there, builds the candidate that the edit describes and diagnoses the complete graph of that candidate. It edits a document that is identified uniquely and has the current node format, and it applies the schema, the size limits and the checks of physical paths to everything it writes. A node in a graph that is invalid elsewhere can be edited, and an edit that leaves the graph invalid is written as well, as a step on the way to a valid graph. `--require-valid` requires in addition that the complete candidate is valid before any node file is written. The writer refuses to delete the manifesto and to give it parents.

The writer stages the new bytes on the same file system as the node files. It writes a journal that records for every changed path the original bytes and the new bytes, or the absence of a file. It compares each file with its original bytes right before it replaces it, and it verifies the files that result. An edit that succeeds and leaves an invalid graph completes like any other and clears its transaction data. The comparison of original bytes is the whole protection among writers that cooperate through the lock.

A write that was interrupted blocks further writes until `recover` has run. Recovery restores the original bytes that it recognizes from the journal, also when the original graph was invalid, reports the diagnostics of the restored graph and removes the journal and the staged files of the transaction it has completed. Text that somebody else wrote into a file in the meantime is kept, and in that case the journal and the staged files of the unfinished transaction stay in place. A lock that a writer left behind is cleared only after it is confirmed that this writer is gone. `init` stages a complete valid graph and publishes it as a whole. The protection against races in the file system and the durability after a loss of power go as far as the guarantees of the file system itself.

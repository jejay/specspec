---
id: MmfPuhY=
type: requirement
parents:
- aILBxDs=
- DFS2oJM=
---
# Distinguish logical node records from physical document evidence

application protocol parsed records carry complete logical bodies with newline encodings normalized
to LF, sorted parent/source fields and unchanged identities. Readable projections
and logical diffs use the same content. Spaces, indentation, blank lines and final
newline presence stay meaningful. Physical newline encoding alone is equivalent.

Raw query documents, native before/after plans, canonical files, immutable Git
blobs, transaction guards and recovery retain exact bytes. New nodes use LF;
existing-document writes adapt body input and replacement NEW to that document's
newline style and append a missing file terminator. Existing trailing blank lines
remain unchanged. Git configuration, attributes and linked source files remain under
their existing owners. Verify logical behavior and physical safety separately.

Application envelopes and canonical node fields retain their contracts. Representation policy
changes do not add a node-format constraint rejecting existing newline encodings.

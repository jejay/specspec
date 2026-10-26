---
id: MmfPuhY=
type: requirement
parents:
- aILBxDs=
- DFS2oJM=
---
# Distinguish logical API records from literal canonical documents

Preserve the API-7 parsed node projection: complete logical body text with CRLF
normalized to LF, sorted parent/source fields and unchanged node identities. JSON
retains logical line/paragraph layout rather than the readable one-line projection.
Raw query documents, canonical files and literal diff evidence carry physical line
endings and bytes. Replacement NEW remains literal in saved files and unmatched
source text stays unchanged. Verify logical and physical representations separately.

Release qualification tests the existing distinction and describes it explicitly;
packaging does not introduce a protocol change or promise byte-identical canonical
text from parsed node records. Semantic records and physical repair/evidence each
retain their own roles.

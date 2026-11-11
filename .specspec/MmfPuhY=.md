---
id: MmfPuhY=
type: requirement
parents:
- qTT_OhY=
---
# Carry logical text in node records and exact bytes in raw reads, plans and safeguards

A node record of the application protocol carries the complete body in logical form with LF line ends, the parents and the sources in sorted order and the ID as it is. Readable output and logical diffs show the same content. Spaces, indentation, blank lines and the presence of a final newline carry meaning. Two texts that differ in newline encoding alone are equal.

Exact bytes are kept in raw `query` documents, in the before and after text of an edit plan for an editor's own document, in the node files, in Git blobs, in the guards of a write transaction and in recovery. A new node uses LF. A write to an existing document turns body input and the NEW part of a replacement into the newline style of that document and appends a missing final newline. Trailing blank lines that exist stay as they are. The Git configuration, the attributes and the linked source files are under their owners' control. Tests check the logical behavior and the safety of the bytes separately.

The node format accepts a document in each newline encoding: LF, CRLF and CR.

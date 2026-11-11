---
id: qTT_OhY=
type: requirement
parents:
- w7A25ZA=
---
# Compare node text with LF line ends and write each document in its own newline style

The logical text of a node is UTF-8 with LF line ends, and CRLF and a lone CR mark the same line boundaries. Node records, changes of node text, patch text, the change hints of `query` and the results that an edit reports are compared in this form. All other characters, indentation, trailing spaces and the number of blank lines are kept. A read or a comparison shows whether a text ends with a newline, whatever a tool would write at the end of a document. Content that cannot be read as UTF-8 is compared byte for byte, and content that is unavailable is reported as unavailable.

An update through the writer and an edit plan for an editor's own document use the newline style of the line that opens the frontmatter for the whole document. A new node uses LF. Text given in `-m` messages, on standard input or as the NEW part of a replacement keeps its content literally, with its newlines turned into the style of the document. Content that a replacement leaves unmatched stays as it is, and so does the metadata. The size limit is checked on the bytes that are actually written in the style of the document, separately from the limits on arguments and input as given.

`diff` shows every meaningful change of node text and metadata, with patch lines that end in LF. A difference in newline encoding alone counts as no change of a node and no change of a file, and no counts of line ends are printed for it. A change in whether a document ends with a newline appears with the ordinary patch marker. A structured record of a file patch carries the counts of CRLF, LF and CR line ends and the presence of a final newline, before and after, wherever the file has a meaningful change. A raw `query` gives the exact bytes of a document.

A read or a comparison leaves the files as they are. The Git configuration, the attributes, the index, the hooks and the filters are under the owner's control, and this normalization happens inside specspec without any setup of the repository and without running a Git filter. Save and undo of a VS Code document belong to VS Code. The checks of original bytes, the journals, recovery, Git blobs and the verification of cached content work on exact bytes.

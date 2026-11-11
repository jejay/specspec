---
id: c2WCD6c=
type: requirement
parents:
- TaNM294=
- P2i_png=
---
# Record a spotlight as metadata with its comparison and a sparse summary of uncommitted changes

A spotlight is one immutable record of metadata: one message, an ordered list of unique full node IDs and a comparison of a base and a target. A Git ref that is named explicitly is resolved to its full commit ID at capture. The default comparison is stored as HEAD against the working files and follows the current HEAD when it is displayed. A record whose target is the working files also stores the HEAD of the capture and a sparse map of every node with uncommitted changes: the SHA-256 checksum of the literal bytes for a node that is added or modified, and a null marker for a node that is deleted. Git tells which saved files are uncommitted, and the unsaved text of open editor documents, which the editor supplies as trusted input, adds its changes. A clean committed node has no entry and is identified through its commit. The record captures drift this way without holding a copy of node text. The summary is taken from the bytes of the files at the node paths, whether or not they parse: an unreadable file that exists has a checksum, and a null marker means that the file is absent.

When a record is displayed, the summary of the working files at that moment is compared with the captured one. Separate warnings report that HEAD moved, that nodes of the working files changed and that the context is unavailable. The warnings advise and block nothing: every selected ID that the displayed target or the deleted part of the base holds is highlighted, missing IDs are reported, and the status added, modified, deleted or unchanged is derived from the displayed comparison. The unsaved text of open editor documents takes part in a capture from an editor and in the warnings, and the draft of a form that the writer saves stays with its form. The checksums are local hints about drift, apart from the node format and from the safeguards of a write.

The local spotlight format has version 2: one metadata file per spotlight, a limited number of records and a limited size of metadata, protection of malformed records, atomic publication and a flush that is explicit and reviewed. A record in an unsupported storage format stays in place, with a diagnostic that says how to flush it. An explicit flush also removes blob files of an unsupported format from the store. The version of the spotlight format is its own, independent of the node format and of the maintained example history.

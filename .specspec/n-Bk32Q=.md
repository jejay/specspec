---
id: n-Bk32Q=
type: implementation
parents:
- rQTg56g=
- RY5LFw8=
sources:
- path: src/specspec/annotation_commands.py
- path: src/specspec/annotations.py
- path: src/specspec/application.py
- path: src/specspec/cli.py
- path: src/specspec/editor.py
- path: tests/test_annotations.py
- path: tests/test_cli_compact.py
- path: tests/test_spotlight_backchannel.py
---
# Store spotlights as local metadata records and warn about drift of the working files

`annotations.py` publishes each spotlight as one immutable record of the local format 2 with a message, node IDs and a comparison, under the lock that the writers of the working files share. An explicit ref is pinned to its commit, and the default comparison of HEAD and working files stays live. The summary of the working files holds a checksum only for nodes that are added or modified without being committed, and a null marker for deleted ones. A capture copies no node text and stores no preview of it. The store is excluded from Git through the local exclude file, a write is refused while Git tracks files of the local state, a malformed record is protected and reported, and a flush that names a reviewed list is refused when the list has changed since the review.

A capture and the store work within these limits:

- 500 characters for a message
- 512 node IDs for one spotlight
- 512 KiB for one record
- 256 records and 4 MiB of metadata for the whole store

`annotation_commands.py` provides `spotlight add`, `spotlight show` and `spotlight flush`. Their arguments are node IDs and one message, in which a color name is ordinary text, with `--base` and `--target` for the comparison. `spotlight show` derives the status and the title of each member from the comparison of its record and reports drift while it keeps every ID that can be matched. The reads of the application protocol in `application.py` and `editor.py` return the sparse state of the working files, from which both graph editors compute their warnings. A spotlight created in an editor uses the unsaved text of open editor documents, which the editor supplies as trusted input, and saves neither a document nor the draft of a form. An explicit flush also removes blob files of an unsupported format from the store, and a record in an unsupported format gets a diagnostic that says how to flush it.

`tests/test_annotations.py`, `tests/test_spotlight_backchannel.py` and `tests/test_cli_compact.py`, on throwaway graphs and on the Gantt history in the current format, cover comparisons pinned to commits and to branches, the selection of added, deleted and unchanged nodes, checksums of the literal bytes for uncommitted nodes only, unsaved editor text, a moved HEAD and drift, absent members and unavailable refs, atomic rejection and publication, immutable messages, the exclusion from Git, the limits on metadata and the races of a reviewed flush.

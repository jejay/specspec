---
id: P2i_png=
type: requirement
parents:
- DG-JpDc=
---
# Keep each spotlight as an immutable file in a store local to the checkout

Each complete spotlight is stored as `.specspec/local/annotations/<shot-id>.json`. This local metadata persists, and the command line and both graph editors share it within one checkout. Where the ignore rules of the project leave the directory unprotected, the local exclude file of Git protects it, and a write is refused while Git tracks files of the local state.

The message, the comparison and the list of nodes are validated against their limits before one immutable file is published atomically, under the lock that the writers of the workspace share. The complete spotlight files are the source of the list. A malformed record is protected and reported with an error that says what to do, and at a limit a new spotlight is rejected while the stored ones stay. An explicit flush removes the spotlight metadata and obsolete blob files and keeps the recovery data and the other local state. Publishing follows the ordinary behavior of lock and recovery.

The public commands are `spotlight add`, `spotlight show` and `spotlight flush`. A capture by the command line reads the saved files, and a capture in an editor includes the trusted text of open documents and the current comparison. A spotlight stores references and, for the working files, sparse data by which later drift is noticed, with an ID and a capture time that are generated independently. Git holds the text of committed nodes.

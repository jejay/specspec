---
id: P2i_png=
type: requirement
parents:
- DG-JpDc=
- _wJJQko=
- 0dvOn3A=
---
# Keep immutable spotlight shots in a checkout-local store

Store each complete addition in .specspec-local/annotations/<shot-id>.json, with
retained node bytes in its blobs subdirectory. This persistent local data belongs
to the SpecSpec checkout and is shared by the CLI and both hosts. Git's local
exclude protects the directory when project ignore rules do not already do so.
Refuse spotlight writes over Git-tracked local-store files.

Validate the entire bounded addition and capture every reference before publishing
one atomic immutable shot. Parallel managed writes serialize; ordinary recovery
retains its lock contract. Complete shot files are the list's source of truth.
Preserve malformed data with actionable errors and reject storage limits rather
than expiring or evicting shots. Explicit flush removes only the spotlight store's
shot files and retained blobs, preserving recovery and other local state.

The public command is spotlight add/show/flush; the UI button is Spotlights.
Add takes colored node sets and a single message directly as CLI arguments.
Capture uses saved workspace bytes by default or one explicit immutable revision.
Internal ordered groups carry the shared message, color and full node IDs with
exact blob addresses. Existing immutable submissions keep their original bytes;
internal paths and keys are independent of public naming. Submissions retain
capture provenance and independently generated shot identity.

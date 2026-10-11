---
id: tvic3PQ=
type: requirement
parents:
- Bnr6yZY=
- DiIJxaQ=
- YOPhqYc=
---
# Use hash-free version-three files and watcher-driven reconciliation

Choose hash-free format/API 3: no managed_hash, snapshot fingerprint, --expect
option or hash verification. The later compact-ID/current-only correction selects
canonical padded Base64url IDs and equals-delimited filenames. Validate only the
current schema; reject superseded formats/UUIDs and unknown metadata rather than
normalizing them or offering migration. The two working graphs were converted once
through a temporary journaled tool; that is not shipped compatibility code.
Root Git history need not remain readable. The Gantt regression history is
explicitly rebuilt under the current scheme; unrelated history stays untouched.

Continue validating schemas and the full rooted DAG, locking tool writers,
comparing original file bytes during replacement and refusing recovery over
external edits. These are consistency and transaction protections, not manual-edit
provenance gates or approval. Git compares semantic records and raw bytes directly.

Coalesce watcher events as reload hints, serialize reads/writes, retry transient
read failures a bounded number of times, and compare loaded data directly to avoid
unnecessary redraws. Use VS Code's filesystem watcher; Electron watches both the
project directory and canonical directory so replacing/deleting/recreating the
latter reattaches its watcher. Surface watcher errors; don't secretly enable polling.
A configurable millisecond interval defaults to zero in both hosts; configuration,
project switches and disposal cancel old timers/watchers. Explicit refresh remains.
No watcher-only guarantee is claimed for every filesystem or arbitrary missed event.

Refresh clean forms. Retain dirty drafts with their original node record, not a
hash; unrelated changes refresh context without preventing saves. Ask confirmation
before saving over a changed edited node, and preserve deleted-node drafts for
copy/discard. Re-read and validate current files before UI mutations. Invalid reloads
retain the last valid graph marked out-of-date with diagnostics, disable mutations
until fixed, and never rewrite the external files. Historical views stay read-only.
Render acknowledgements use session sequence tokens and full visible membership,
not content hashes. External editors need not honor locks, so final byte comparison
and atomic replacement reduce but do not eliminate every filesystem race.

Origin: a revisable technical conclusion implementing the user's new intention;
versioning, conflict confirmation and watcher adapters do not rewrite its outcome.

---
id: 93224022-0c11-4260-b09e-2925b7aacf0f
type: requirement
parents:
- 5c2b23ba-7bbc-4458-b63e-808e58cd7059
- 4d1f2eee-8125-4e3f-b9b4-649517875d87
- 65f28474-18be-46f8-89f6-b9ce30a0ec96
---
# Use hash-free version-three files and watcher-driven reconciliation

Choose format/API version 3: no managed_hash, snapshot fingerprint, --expect option,
or hash verification even for older readable revisions. Recognize legacy v1/v2
hash fields only as ignored compatibility metadata; normalize old approval fields
as before. An explicit journaled migrate converts older working graphs to v3,
removing obsolete metadata while preserving IDs, paths, bodies, links, sources,
extensions and unaffected comments. Never rewrite historical Git blobs.

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

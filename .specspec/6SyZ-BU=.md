---
id: 6SyZ-BU=
type: requirement
parents:
- ME4UXTA=
---
# Journal safe explicit edits independently of graph validity

Under a project workspace lock, inventory actual canonical files, construct the
explicit candidate and diagnose its complete graph. Managed edits target uniquely
identified current-format documents and have schema, bounded-input and physical
path safeguards. Invalid surrounding graphs and intermediate graph-invalid results
remain editable; --require-valid additionally requires a valid complete candidate
before any canonical write. A parent ID that an edit introduces names a node of the final candidate, so a mistyped parent is rejected before writes; parent references that a node already declares stay editable. The manifesto is protected from deletion/reparenting.

Stage bytes on the same filesystem, journal original/replacement/absence states,
compare original bytes before replacement and verify resulting files. A successful
graph-invalid edit completes and cleans its transaction normally. Original byte
checks, not node fingerprints or approval tokens, protect cooperating writers.

Interrupted batches block writes until recover. Recovery restores recognized original
bytes even when the original graph was invalid, reports its diagnostics and cleans
completed transaction state. Preserve intervening external text and unfinished data.
Clear stale locks only after confirming the writer absent. Writers and reads that find another writer's lock wait a few seconds for it. A lock that remains is reported as either a running edit or a stale lock that recover --force-lock clears, and reads report a remaining lock or interrupted edit by that cause. Init publishes an entire
valid staged directory. Staged bytes and the journal are flushed to disk before the first canonical change, so an unreadable journal means that no node changed: recovery removes it with the staged files, restores nothing and says so. Filesystem races are bounded.

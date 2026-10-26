---
id: 6SyZ-BU=
type: requirement
parents:
- tvic3PQ=
---
# Journal safe explicit edits independently of graph validity

Under a project workspace lock, inventory actual canonical files, construct the
explicit candidate and diagnose its complete graph. Managed edits target uniquely
identified current-format documents and retain schema, bounded-input and physical
path safeguards. Invalid surrounding graphs and intermediate graph-invalid results
remain editable; --require-valid additionally requires a valid complete candidate
before any canonical write. The manifesto stays protected from deletion/reparenting.

Stage bytes on the same filesystem, journal original/replacement/absence states,
compare original bytes before replacement and verify resulting files. A successful
graph-invalid edit completes and cleans its transaction normally. Original byte
checks, not node fingerprints or approval tokens, protect cooperating writers.

Interrupted batches block writes until recover. Recovery restores recognized original
bytes even when the original graph was invalid, reports its diagnostics and cleans
completed transaction state. Preserve intervening external text and unfinished data.
Clear stale locks only after confirming the writer absent. Init publishes an entire
valid staged directory. Filesystem races and power-loss durability remain bounded.

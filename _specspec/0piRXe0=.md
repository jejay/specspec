---
id: 0piRXe0=
type: requirement
parents:
- -RQn7Ug=
---
# Apply explicit intermediate edits with an optional valid-result boundary

add/update/delete operate on safe uniquely identifiable current-format targets while
allowing graph-invalid surrounding and resulting states. Diagnose the complete result
and emit an applied receipt with validity/completeness; graph invalidity alone is not
operation failure. --require-valid rejects the whole proposed invalid result before
writes. check remains strict, including staged sources and independent usable mappings.

Advanced apply --edits-json accepts bounded explicit add/update/delete edits with
inline bodies and local aliases for newly allocated identities. Integration --plan
accepts files/stdin and body files relative to the plan (stdin uses launch directory).
Reject ambiguous/conflicting edits and apply the complete
candidate in one recoverable transaction, with non-writing --dry-run. Aliases and
plans create no canonical metadata, identity reservation or approval gate. Deletion
consent and physical transaction checks remain effective in batches.

API 7 coordinates these semantics across CLI and hosts while node format 7 stays
unchanged. Exit zero means an operation/read was delivered, one means failed check
or rejected request, and two means invocation/I/O failure. Explicit incomplete reads
retain available evidence with nonzero status; diagnostics never conceal saved edits.

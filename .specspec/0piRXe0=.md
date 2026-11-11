---
id: 0piRXe0=
type: requirement
parents:
- -RQn7Ug=
---
# Apply explicit intermediate edits with an optional valid-result boundary

The add, update and delete commands operate on safe, uniquely identifiable targets
while
allowing graph-invalid surrounding and resulting states. Diagnose the complete result
and emit an applied receipt with validity/completeness; graph invalidity alone is not
operation failure. --require-valid rejects the whole proposed invalid result before
writes. check is strict, including staged sources and independent usable mappings.

One invocation may combine bounded explicit add/update/delete steps, literal
messages, integration body inputs and local aliases for newly allocated identities.
Parse the complete editing grammar before input reads or writes. Reject mixed
non-editing commands and ambiguous/conflicting edits. Save the complete candidate
in one recoverable transaction, with non-writing --dry-run and optional final
validity. Aliases create no canonical metadata, identity reservation or approval
gate. Deletion consent and physical transaction checks are effective in chains.

The application protocol carries these semantics to the CLI and hosts. Exit codes follow the application protocol. Explicit incomplete reads
retain available evidence with nonzero status; diagnostics never conceal saved edits.

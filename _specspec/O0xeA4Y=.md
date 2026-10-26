---
id: O0xeA4Y=
type: implementation
parents:
- 1GJRSPU=
sources:
- path: src/specspec/body_replacements.py
- path: src/specspec/cli.py
- path: src/specspec/edit_cli.py
- path: src/specspec/batch.py
- path: tests/test_cli_replacements.py
- path: tests/test_cli_chains.py
- path: tests/test_transactions.py
- path: docs/cli.md
- path: docs/investigations/exact-replacements.md
---
# Implement exact body replacements through the existing candidate writer

cli.py parses repeatable OLD/NEW arguments, rejects mixed body sources and exposes
replacement updates through the shared explicit-edit planner. edit_cli.py consumes
the complete two-value option arity, including an attached OLD, before callbacks.
Literal command/flag words remain values rather than accidental step boundaries.

body_replacements.py validates nonempty bounded pairs and locates each unique OLD
in one original body, including overlapping-occurrence ambiguity checks. Disjoint
spans build a single bounded UTF-8 result with literal NEW and unchanged surrounding
characters. batch.py charges both sides with other body input before auxiliary
reads and applies each transformation to the fresh node under the writer lock.
The existing serializer, complete-candidate validity, deletion consent, original
bytes, journal and recovery retain their owners. UI transports and API/format 7
remain unchanged.

Regression tests cover exact and simultaneous matching, ambiguity/overlap, empty
and no-op pairs, source conflicts, body/metadata separation, field association,
argument arities, UTF-8/EOL and payload/result limits, previews and invalid graphs,
combined alias/deletion repair, fresh locking, byte races and interruption recovery.
Windows subprocesses retain multiline Unicode argv under legacy output encodings.
The linked investigation records completed verification and platform boundaries.

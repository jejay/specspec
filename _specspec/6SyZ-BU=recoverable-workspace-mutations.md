---
id: 6SyZ-BU=
type: requirement
parents:
- ME4UXTA=
- tvic3PQ=
---
# Validate and journal managed workspace mutations

Under a project workspace lock, load and validate the saved graph, construct the
candidate and validate it before canonical replacement. Stage replacement bytes
on the same filesystem and journal original/replacement states in `.specspec-local`.
Compare each target's original bytes immediately before replacement and validate
again afterward. A null replacement records physical deletion.

Interrupted batches block managed writes until recovery. Recovery restores known
original states only while current files match a known original/replacement/absence
state; intervening external text requires explicit user resolution. Preserve the
journal and staged data until completed recovery. Remove a stale lock after confirming
its writer absent. Initialize an entire staged directory from supplied manifesto
text and expose it at `_specspec` once valid. Existing projects use ordinary edits.

These safeguards address cooperating writers and process interruption. Filesystem
races and full power-loss durability require their own assessment.

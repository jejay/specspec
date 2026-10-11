---
id: apEb_pM=
type: requirement
parents:
- 3wsnEjk=
- VZvwDBY=
- _wJJQko=
- _yahyM4=
- DiIJxaQ=
- ME4UXTA=
- SRsw2W0=
---
# Use Git newness and a withdrawal flag, not approval states

Ordinary nodes have no stored review stage. Optional retired: true records withdrawal
only; retain old text and relationships as history. Keep the manifesto non-retired
and prevent live nodes from depending on withdrawn parents. Explicit retire/restore
commands change withdrawal, never acceptance or confidence. No accept command,
approval filter, score, parent-review prerequisite or receipt gate is introduced.
Git additions/changes/removals/renames and linked-source impact remain derived.

This choice originally introduced format/API 2; the later hash-free correction
selected version 3, and the current compact-ID conclusion now defines its sole
supported node schema. Retain this reasoning as withdrawal/Git-newness context,
not a requirement for v1/v2 readers or migration. Superseded fields and ID schemes
are rejected, not normalized. Current writes keep structural/transaction checks
without provenance enforcement; no history compatibility gate is introduced.

Origin: the separate risk-proportionate-review conclusion originally selected
version two; the user's later consenting-adults correction withdraws its hash
requirements. Schema versions and migration mechanics remain revisable choices.

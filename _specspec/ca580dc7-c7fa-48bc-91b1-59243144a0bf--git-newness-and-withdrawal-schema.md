---
id: ca580dc7-c7fa-48bc-91b1-59243144a0bf
type: requirement
parents:
- a3cad33b-c1f9-4903-8394-9e6cd3cc5b73
- c0943883-e3cb-4de9-8c5e-6aeb4a37dd06
- 955b905a-6220-4d5c-b0ca-fab86b6b6db8
- 95287a17-697f-43ad-80b0-140d5e0ec058
- 4d1f2eee-8125-4e3f-b9b4-649517875d87
- 003d697b-4104-4fdf-8e05-0db572c436d0
- 51c3e963-674e-4d5d-bd7a-b8d63649e1c8
---
# Use Git newness and a withdrawal flag, not approval states

Ordinary nodes have no stored review stage. Optional retired: true records withdrawal
only; retain old text and relationships as history. Keep the manifesto non-retired
and prevent live nodes from depending on withdrawn parents. Explicit retire/restore
commands change withdrawal, never acceptance or confidence. No accept command,
approval filter, score, parent-review prerequisite or receipt gate is introduced.
Git additions/changes/removals/renames and linked-source impact remain derived.

This choice originally introduced format/API 2 to remove proposed/accepted fields.
The user's later manual-edit correction supersedes that writer/API and all managed
hash/fingerprint requirements: the separate hash-free-schema-and-watcher-reconciliation
conclusion chooses format/API 3. Read legacy v1/v2 as normalized approval-free
records, ignore old hashes, and never rewrite historical Git bytes. An explicit
journaled migrate removes obsolete hash/approval metadata from a working graph
while preserving IDs, paths, bodies, links, sources, extensions and comments.
Recovery restores the complete original schema, without overwriting external edits.

Legacy workspaces offer migration, not historical views or dirty drafts. Save nodes
without an approval stage, keep withdrawal controls separate, and use meaningful
non-approval colors. Manual changes are permitted; structural checks and tool
transaction protections remain, without provenance enforcement or --expect.

Origin: the separate risk-proportionate-review conclusion originally selected
version two; the user's later consenting-adults correction withdraws its hash
requirements. Schema versions and migration mechanics remain revisable choices.

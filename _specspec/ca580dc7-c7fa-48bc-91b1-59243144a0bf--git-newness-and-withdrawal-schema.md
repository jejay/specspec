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
managed_hash: a9613cb6dbc3f5053d5b88ca28f72af6133ca309ab0b9fae9bbf534cee3caa2e
---
# Use Git newness and a withdrawal flag, not approval states

Use version-two frontmatter with no status field. Ordinary nodes have no stored
review stage; an optional boolean retired flag records withdrawal only. Retain
withdrawn text and relationships as history, keep the manifesto non-retired, and
prevent non-retired nodes from depending on withdrawn parents. Explicit retire
and restore commands change withdrawal, never acceptance. Restore does not claim
that a decision has been reviewed. There is no accept command or approval filter.

Keep UUID identities, incoming parents, strict typed metadata, managed integrity,
locking, guarded fingerprints, and recoverable writes. Advance the JSON API to
version two, exposing retired booleans rather than approval status. Context export
includes live siblings without classifying them as proposed. Git added/changed/
removed/renamed labels and linked-file impact remain derived comparisons.

Provide an explicit fingerprint-guarded migrate command for version-one graphs.
Validate the original hashes with their original canonicalization before converting
all nodes in one journaled transaction. Preserve IDs, paths, parent links, body
bytes, source references, extension metadata, and unaffected comments; map legacy
retired to the withdrawal flag and discard accepted/proposed without manufacturing
approval evidence. Reject ordinary writes to unmigrated workspaces with guidance.
Keep legacy Git revisions readable and normalize them to the approval-free model
for comparison; never change historical files or bless an unmanaged edit. Recovery
must restore the whole original version after an interrupted migration.

The editor offers migration for an editable legacy workspace, but not historical
views or while a draft is dirty. Remove acceptance controls and proposal wording.
Use distance-first fills and the existing node types as an alternate presentation
mode, keeping withdrawn labels and Git accents distinct. Do not introduce an
active/approved replacement status, confidence slider, or receipt gate.

Origin: a separate implementation conclusion addressing the user's review-budget
intention; schema/API versions, withdrawal encoding, migration, and palette modes
are technical choices rather than prescribed confidence levels.

---
id: AuhoBoU=
type: requirement
parents:
- fuyy0Lk=
- 5d5oDCM=
- 6SyZ-BU=
---
# Plan and delete the entire downstream closure, with pre-deletion Git warnings

Implement fuyy0Lk= as a correction of 5d5oDCM='s earlier named-files-only choice.
Keep format/API 5 and its physical-deletion/HEAD-ghost/native persistence contract;
no canonical field, fingerprint, legacy reader or review workflow is introduced.

Compute the union of each explicitly requested node and ALL directed descendants
in the current valid saved DAG. Traverse iteratively and deduplicate by ID. A child
with ANY selected/deleted parent belongs to this closure even if another parent
survives. Its descendants belong too. Do not use the UI placement backbone,
all-parent/exclusive-ownership criteria, distance, Git base graph or source impact
to decide membership. Outside parents/ancestors and unrelated branches survive;
never silently reparent. Refuse manifesto/unknown IDs, empty or duplicate root
arguments and invalid graphs before any canonical write. Overlapping distinct
requests are allowed, with each affected file deleted once. Validate the remainder.

Derive uncommitted warnings from ordinary Git working/index changes for every
selected or descendant node's canonical path, not only the clicked node and not
from semantic M alone. Include untracked/ignored additions, staged additions,
unstaged/staged changes (also comment/format-only changes), renames, mode changes
and unmerged entries. A staged node is still uncommitted. Do not warn a committed
node solely because linked implementation CODE changed. Ask Git without optional
index writes and use NUL-delimited paths/nested-project prefixes. Git's own clean
filter/line-ending interpretation applies; no new node hashes are stored. Git
metadata/features can hide changes, so no adversarial detection guarantee is made.
No Git/unavailable assessment warns explicitly for the whole affected set rather
than asserting those nodes are committed; unborn HEAD nodes are uncommitted.

Offer delete --dry-run [--json] as a non-writing plan with requested_ids,
deleted_ids, id/path pairs, per-node Git status and assessment/warning details.
Return all actually deleted IDs on success (including implicit/shared children),
not merely arguments. Human CLI shows warnings BEFORE any unlink and asks one
whole-action confirmation when warnings exist. JSON/noninteractive use with
warnings refuses to delete unless --yes explicitly consents; --yes never hides
warnings. Clean committed CLI batches need no extra ceremony. Cancellation/refusal
changes no canonical files and creates no unfinished journal. This is destructive
operation consent, not confidence, acceptance or a per-node review gate.

Both UI hosts obtain this same backend plan, show cascade size (including shared
children) and every uncommitted warning in their existing native confirmation,
then invoke managed deletion with --yes and the reviewed plan as bounded JSON stdin.
The writer replans under its ordinary lock, compares requested/affected IDs, paths
and warning/assessment records directly, and refuses a changed scope or new warning
before unlinking. CLI --reviewed-plan is transaction-scope protection, not a hash,
--expect, staged baseline or persistent approval receipt. The plan does not freeze
all file text/HEAD or prove lineage: ordinary original-byte checks still protect
the actual deletion transaction, and noncooperating writers can race it. No hidden
retry deleting an enlarged closure after confirmation. Native dirty SpecSpec
documents remain protected project-wide; per-view drafts/errors/cancellation stay
copyable. A descendant tab cannot edit an absent file or resurrect an overlay.

Unlink the entire closure in the existing new=null journaled batch. Recovery retains
original bytes for implicit descendants too and refuses external replacements.
No auto-staging/commit, source deletion, Git object/ref/index mutation, root deletion
or automatic cascade on manual filesystem edits. HEAD-relative committed ghosts
persist through staging and vanish on commit; never-committed descendants have
no fabricated HEAD ghosts. Historical comparisons remain independent/read-only.

Verify sole-parent and multi-parent children, deeper shared descendants, overlapping
requests, long iterative DAGs, complete reported IDs and preserved outside parents;
warning on only a descendant, new/staged/unstaged/ignored/renamed/comment-only nodes,
clean/source-only cases, unborn/non-Git/nested repositories; pre-write warning and
cancel/--yes/JSON behavior, plan changes, byte races/interruption/recovery; both host
confirmation/native protections and whole-cascade HEAD/stage/commit lifetime in
independent current-schema Git fixtures. No schema conversion/full-history rewrite
is needed here; retained Gantt deletion receipts must still reflect valid closures
under current tools. Passing tests are evidence, not semantic or filesystem proof.

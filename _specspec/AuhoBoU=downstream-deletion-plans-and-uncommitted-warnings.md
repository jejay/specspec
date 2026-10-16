---
id: AuhoBoU=
type: requirement
parents:
- 5d5oDCM=
- 6SyZ-BU=
---
# Plan a descendant cascade and warn before losing uncommitted files

Union explicitly requested roots and all directed descendants of the current valid
saved DAG, iteratively deduplicated by ID. A child with any deleted parent belongs,
including shared/partial children and deeper descendants. Distinct overlapping
roots are valid. Reject empty/duplicate/unknown/manifesto requests and invalid
snapshots before canonical writes. Validate the remainder, preserving surviving
outside parents and unrelated records byte-for-byte.

Assess each affected canonical path using NUL-delimited ordinary Git status with
literal nested-project paths, optional Git locks/index refresh disabled and fsmonitor
disabled. Warn for untracked/ignored additions, staged additions/edits, unstaged
changes, comment/format-only changes, renames, modes and unmerged entries. Assessment
uses Git clean-filter/line-ending interpretation. Node warnings follow node-file
changes; code-only source impact is separate. Unborn additions warn; missing/failed
Git assessment warns explicitly for the entire scope. Git settings/flags bound this
assessment's reliability.

`delete --dry-run` returns requested_ids, deleted_ids, ID/path nodes, per-node
uncommitted statuses, git_available and git_note. Emit warnings before unlinking.
Human warned deletion asks one whole-action confirmation; warned JSON/noninteractive
actions require `--yes`. Consent retains stderr and JSON warning diagnostics. Clean
committed CLI batches proceed. Cancel/refusal retains canonical files and a completed
transaction state. Success reports every actually removed ID.

Both hosts show the backend scope/shared-child count and warnings in confirmation,
then submit explicit consent and the reviewed plan through bounded integration input. Replan under the writer
lock and compare requested/affected IDs, paths and assessment records directly;
a changed plan fails `DELETE_PLAN_CHANGED` before unlinking. Original-byte checks
protect the ensuing transaction. Native dirty documents remain project-wide protected.

Journal each descendant with `new: null`, preserving originals for recovery. Reject
intervening external text. Source files and Git staging/commits remain under owner
control. Committed cascade D ghosts persist through staging until commit; uncommitted
additions retain their actual empty HEAD membership. Manual deletions receive normal
consistency diagnostics. Filesystem races retain the writer's stated limitations.

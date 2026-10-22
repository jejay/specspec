# Removing nodes and the default workspace graph

**Withdraw by deleting node files.** There is no retired flag, retire/restore
command, live/retired filter or withdrawal badge in current node format **7** / API **6**.
Earlier text and relationships remain in Git history. Explain your reason in the
normal Git commit, rather than maintaining a separate lifecycle state.

## Delete the entire descendant closure

```sh
specspec delete <id> [<another-id> ...] --dry-run --json
specspec delete <id> [<another-id> ...]
# Noninteractive/JSON consent when the preview warns about uncommitted nodes:
specspec delete <id> [<another-id> ...] --yes --json
# Review, stage and commit yourself. Explain the removal in the commit message.
```

Delete removes each requested node **and every child at every depth**, including
**partial/shared children** with other surviving parents. Those children's own
children are deleted too. Multiple paths and overlapping requested roots remove
each file once. Outside parents, ancestors and unrelated branches survive; the
command never silently reparents. The saved graph determines the closure, not a
layout backbone, exclusive ownership, Git base graph or source impact.

The manifesto cannot be deleted. Invalid graphs, unknown IDs, empty/duplicate root
arguments fail before any unlink. The remaining specification must be a valid
rooted DAG. Manual filesystem deletion remains permitted, but is NOT an automatic
cascade; invalid external deletions produce diagnostics, not graph repair.

## Warn before discarding uncommitted nodes

Every affected node is checked, not just the named node. Added/untracked/ignored
nodes, staged additions, staged or unstaged edits, comment-only changes, renames,
mode changes and unresolved index entries warn. **Staging is not committing.**
Changed linked code alone is not an uncommitted-node warning. Ordinary Git status
uses its own clean-filter/line-ending interpretation; Git flags/configuration can
hide changes, so this is not adversarial detection or a new node-fingerprint scheme.
Unborn HEAD nodes are uncommitted. Without Git or a usable assessment, the whole
closure is warned about explicitly instead of being declared committed.

`--dry-run` writes no files and returns a plan: `requested_ids`, `deleted_ids`, all
`nodes` (ID/path pairs), per-node `uncommitted` Git statuses, `git_available` and
`git_note`, plus structured warning diagnostics. Success reports ALL removed IDs
in `changed_ids`/`deleted_ids`, including implicit descendants.

An interactive terminal asks one whole-action confirmation when warnings exist;
cancelling leaves every file intact. JSON/noninteractive calls with warnings fail
without deletion unless `--yes` explicitly consents. Clean committed CLI branches
need no extra confirmation. `--yes` does not hide warnings: stderr receives them
before unlinking, and JSON stdout remains one envelope with the same diagnostics.
These are destructive-action warnings/consent, not confidence or approval states.

Both UIs preview through the same backend and confirm the total closure size,
shared-child rule and warnings before deletion. They pass the reviewed plan as
bounded JSON stdin (`--yes --reviewed-plan -`). The writer recomputes scope and
warning/path records under its lock; a changed plan fails before writes and needs
another preview/confirmation. It compares actual records, not hashes, `--expect`
or a persistent approval receipt. This does not freeze all text or HEAD; normal
transaction byte checks and filesystem race limitations still apply.

Managed batches retain original-byte checks, lock/journal/recovery and `new: null`
entries for implicit descendants too. If interrupted, keep `.specspec-local` and
run `recover`; it refuses to replace new external text. These are not filesystem-
atomic or adversarial guarantees. SpecSpec never stages/commits, deletes linked
source files or installs hooks for this operation.

## HEAD is the default baseline, not the index

| Situation | Default workspace view |
| --- | --- |
| Node exists in HEAD and workspace | Normal node, with any M changes |
| HEAD node's file deleted | Base node remains as **D**, with earlier links/text |
| Deletion staged | Still **D**: HEAD has not changed |
| Deletion committed | Node disappears from the default view |
| New untracked node created then deleted | No ghost: it never belonged to HEAD |
| Explicit old/new commit comparison | Earlier deleted nodes can still appear |

These rules apply to the entire cascade. Deleted ghosts are display records from
the base revision, not canonical nodes or stored statuses. They cannot be saved,
deleted again or captured into source metadata. Their text remains read-only and
selectable; implementation sources can be previewed against the base code version.
Relationships/metrics use their own revisions, not an invalid union DAG. Dirty
out-of-band forms for a deleted node stay copyable/unsavable even after commit;
keeping a draft is not keeping the canonical node.

Both hosts reread HEAD and watch its private/current-branch/shared packed refs as
well as canonical files, including detached HEAD and linked worktrees. No default
polling. Optional polling and **Refresh** remain for filesystems that miss events;
watch notifications are hints, not a universal delivery guarantee. **HEAD / workspace**
resets an explicit comparison to the default. Each view's comparisons/cameras remain
independent; a historical commit target is read-only.

A genuinely unborn repository uses an explicit empty baseline. A non-Git project
still works without comparison, with a clear note. Invalid/obsolete HEAD graphs are
not silently normalized or called a successful comparison. Only the current schema
is supported; use the independent current-schema Gantt history for temporal tests.

## Native node-file editors

VS Code Delete is a managed, confirmed cascade, not a retired-field edit waiting
for native Save. Save/revert dirty SpecSpec documents first, including descendant
tabs; queued form edits are drained and the action is bound to this tab's node.
Ordinary native Save/undo remains native. An open buffer can outlive a deleted
file, but cannot re-overlay or recreate it in the graph. Attempted graph edits/
saves report the missing file rather than silently resurrecting it.

The physical-deletion/HEAD intention and amended conclusion are
[`xu6W0c4=`](../_specspec/xu6W0c4=.md)
and [`5d5oDCM=`](../_specspec/5d5oDCM=.md).
The follow-up cascade/warning intention and separate detailed conclusion are
[`fuyy0Lk=`](../_specspec/fuyy0Lk=.md)
and [`AuhoBoU=`](../_specspec/AuhoBoU=.md).
Previous explanations remain in Git. This extension does not change node schema;
the complete independent Gantt current-schema history/receipts remain the regression
corpus. Existing manual clones and local experiments are never reset automatically.

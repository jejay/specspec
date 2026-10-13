# Removing nodes and the default workspace graph

**Withdraw by deleting the node file.** There is no retired flag, retire/restore
command, live/retired filter or withdrawal badge in current format/API **5**.
Earlier text and relationships remain in Git history. Explain your reason in the
normal Git commit, rather than maintaining a separate lifecycle state.

```sh
specspec impact <id> --json
specspec delete <id> [<another-id> ...] --json
# Review, stage and commit yourself. A commit message can explain the removal.
```

Delete removes only explicitly named Markdown files. The remaining specification
must be a valid rooted DAG: no dangling parents, implicit cascade or reparenting.
Repair surviving references first or explicitly delete the dependent batch. The
manifesto cannot be deleted by this command. Manual deletion is permitted too;
invalid external deletions produce diagnostics, not an automatically repaired graph.
Managed batches retain original-byte checks, lock/journal/recovery and `new: null`
entries. If interrupted, keep `.specspec-local` and run `recover`; it refuses to
replace new external text. These are not filesystem-atomic or adversarial guarantees.

## HEAD is the default baseline, not the index

| Situation | Default workspace view |
| --- | --- |
| Node exists in HEAD and workspace | Normal node, with any M/R changes |
| HEAD node's file deleted | Base node remains as **D**, with earlier links/text |
| Deletion staged | Still **D**: HEAD has not changed |
| Deletion committed | Node disappears from the default view |
| New untracked node created then deleted | No ghost: it never belonged to HEAD |
| Explicit old/new commit comparison | Earlier deleted nodes can still appear |

Deleted ghosts are display records from the base revision, not canonical nodes or
stored statuses. They cannot be saved, deleted again or captured into source metadata.
Their text remains read-only and selectable; implementation sources can be previewed
against the base code version. Relationships/metrics use their own revisions, not an
invalid union DAG. Dirty out-of-band forms for a now-deleted node remain copyable and
unsavable even after commit; keeping a draft is not keeping the canonical node.

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

VS Code Delete is a managed, confirmed project-file deletion, not a retired-field
edit waiting for native Save. Save/revert dirty SpecSpec documents first; queued
form edits are drained and the action is bound to this tab's node. Ordinary native
Save/undo remains native. An open buffer can outlive a deleted file, but cannot
re-overlay or recreate it in the graph. An attempted edit/save through the graph
reports the missing file rather than silently resurrecting it.

The user intention and separate technical conclusion are
[`xu6W0c4=`](../_specspec/xu6W0c4=withdraw-by-file-deletion-and-show-workspace-against-head.md)
and [`5d5oDCM=`](../_specspec/5d5oDCM=physical-deletion-and-head-relative-ghost-views.md).
Previous retirement explanations now live in earlier Git commits. All maintained
Gantt revisions/refs, actual receipts, ledgers and bundle are reconstructed as if
this deletion-only schema had always been used; manual clones are never reset.

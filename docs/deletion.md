# Exact node deletion and HEAD-relative context

Withdrawing a node physically removes its canonical Markdown file. Canonical node
format **7** has no retired flag, approval state or tombstone. Application API is
**7**. Earlier text/relationships and removal reasons belong in ordinary Git history.

## Delete exactly the selected files

```sh
specspec delete <id> [<another-id> ...] --dry-run --json
specspec delete <id> [<another-id> ...]
specspec delete <id> [<another-id> ...] --yes --json
specspec delete <id> --require-valid
```

Only explicitly named nodes are removed. Surviving shared and exclusive descendants
retain their files, binding text and parent declarations byte-for-byte. A missing
parent is a structural error and a reason to reconsider potentially dependent
reasoning, not permission to delete or silently reparent that reasoning.

Preview reports `requested_ids`, `deleted_ids`, selected ID/path `nodes`, per-file
`uncommitted` statuses, `git_available`/`git_note`, resulting `graph_valid`, broken
references, potential surviving descendants and analysis completeness. No canonical
files are written. All selected IDs must be distinct, known and unambiguous. The
manifesto cannot be deleted. There is no cascade option.

Invalid surrounding graphs and graph-invalid results remain inspectable/editable.
`--require-valid` adds a complete final-candidate check before any canonical write.
See [invalid-graph inspection and repair](invalid-graphs.md) for contextual query/diff,
explicit repair choices, batch application and success/validity distinctions.

## Warn before discarding uncommitted selected files

Selected paths are assessed using ordinary NUL-delimited Git status. Added/untracked/
ignored files, staged additions/edits, unstaged changes, comments, renames, modes and
unmerged entries warn. Staging is not committing. Unselected descendants are retained,
so their uncommitted edits are not destructive-action warnings. Linked-code changes
alone are not node-file warnings. Unknown/unavailable Git assessment warns explicitly.
Git clean filters, EOL interpretation and owner Git flags bound this assessment.

Warnings are delivered before unlinking. Warned terminal actions ask one whole-action
confirmation; warned JSON/noninteractive calls need `--yes`, which retains warnings.
Cancel/refusal removes nothing. Clean committed selections need no extra ceremony.

Both hosts confirm the exact scope and retained unresolved dependencies. They submit
the reviewed plan through bounded `--reviewed-plan -` stdin. The writer recomputes
scope, paths, structural consequences and assessments under its lock; changed records
fail `DELETE_PLAN_CHANGED` before writes. This is a transient consent check, not a
node fingerprint, saved approval receipt or frozen workspace.

The writer journals each selected `new: null`, byte-checks originals and preserves
intervening external text. Interrupted edits require `recover`; recovery can restore
an invalid original graph without treating structural faults as unfinished recovery.
Path/symlink safety, native dirty-document guards and physical race limitations remain.
SpecSpec never stages/commits, installs hooks or deletes linked source code implicitly.

## Default workspace compares to HEAD, not the index

| Situation | Default workspace context |
| --- | --- |
| Node exists in HEAD and workspace | Current binding with any M changes |
| Committed node file is removed | Read-only D record with earlier text/links |
| Deletion is staged | D remains: HEAD has not changed |
| Deletion is committed | Default D membership disappears |
| Survivor still references the missing identity | Current missing endpoint remains visible |
| Never-committed node is created then removed | No fabricated historical D text |
| Explicit earlier base/target | Earlier records remain available from those revisions |

Historical records do not restore current justifications. Missing/unreadable endpoints
are distinct from deleted historical records. Dirty forms for missing files remain
copyable and unsavable; native buffers cannot silently recreate deleted nodes.
Per-revision host metrics do not use a fabricated union DAG. Explicit comparisons
remain independent and historical targets remain read-only.

Canonical/Git watchers reread fresh files and HEAD, including linked worktrees and
shared refs. Notifications are hints; Refresh and optional default-off polling remain
fallbacks. Unsupported historical node schemas stay unsupported. Use the independent
maintained Gantt history for serious temporal and host tests, not obsolete SpecSpec
development snapshots or the tracked non-Git example fixture directory.

The [owner intention](../.specspec/fuyy0Lk=.md),
[plan/safety choice](../.specspec/AuhoBoU=.md) and
[implementation mapping](../.specspec/huB7hcg=.md) describe this behavior.

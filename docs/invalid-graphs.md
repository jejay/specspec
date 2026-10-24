# Inspecting and repairing broken justifications

A valid completed specification is a rooted, shortcut-free DAG. Its working files
can temporarily violate those graph rules. SpecSpec keeps three questions separate:
**did the operation succeed, is the graph valid, and what reasoning may be affected?**
The last question identifies potential scope, not a verdict about owner intent or
semantic correctness. Canonical node format remains 7; the CLI and both hosts use
application API 7.

## Delete precisely what you select

```sh
specspec delete <parent-id> --dry-run
specspec delete <parent-id>
specspec delete <first-id> <second-id>
```

Delete removes exactly those files. All other files and their parent declarations
remain untouched, including shared and exclusively dependent conclusions. A child
can retain a missing-parent error while remaining reachable through another parent.
Its descendants may deserve reconsideration without having a local missing parent.

The preview distinguishes selected deletions, surviving unresolved references,
potential surviving descendants, resulting validity and analysis completeness.
Uncommitted-file warnings concern the files actually being removed. Staged edits
remain uncommitted; warned noninteractive calls need `--yes`. Both hosts confirm the
same backend plan and recheck it under the writer lock. There is no cascade flag.
The manifesto remains protected from deletion or reparenting.

Earlier committed records remain read-only D context against HEAD through staging.
After commit their default D membership disappears, while surviving references still
show missing endpoints. Choose an earlier comparison base to recover earlier text.
A historical record is context, not a restored current justification.

## Discover and inspect

```sh
specspec check --json
specspec show
specspec show <child-id>
specspec show <child-id> --dependents
specspec query
specspec query --issues --with-ancestors
specspec query <child-id> --max-distance 0 --with-ancestors
```

`check` remains strict and exits 1 on invalidity. Its structured result reports
missing/unreadable references, issue-owning nodes, potential descendants and
completeness. It does not mark those descendants for deletion or approval.
`check --sources` also resolves usable implementation mappings when other graph
errors exist; `check --staged --sources` checks the exact index.

`show` reads identifiable current-format nodes without requiring the rest of the
graph to be valid. An unsafe canonical directory, unsupported format, runtime lock
or unfinished transaction still blocks interpreted managed operations. Missing or
unreadable manifesto/schema information needs raw repair rather than guessed parsing.

`query` preserves current and deleted bindings, disconnected components and finite
cycle-safe readings. Missing identities have explicit display placeholders. Those
placeholders are not canonical nodes. `--issues` selects structural findings,
missing identities and potential descendants; `--with-ancestors` adds context.
Use `--issues` without metric criteria. An optional node argument limits issue
selection to that node's reachable context.

Rooted metric selections require enough parsed information to establish their
scope. Shortest paths and unique reachability remain finite on cyclic scopes;
maximum distance is unavailable there and receives a METRIC error. CLI selection
uses its selected-record comparison projection, so earlier records remain explicitly
historical context; it is not a claim about a repaired current DAG. Host card metrics
continue to use the individual original revisions and known relationships.

### Raw, staged and historical reads

```sh
specspec show <node-id> --raw
specspec show --raw --path _specspec/<node-id>.md
specspec show <node-id> --staged
specspec show <node-id> --ref <revision>
specspec query <deleted-id> --base <before> --target <before> --with-ancestors
```

Raw JSON retains literal UTF-8 text, including CRLF and malformed frontmatter. A
non-UTF-8 file has an explicitly labeled Base64 byte result. Human output escapes
terminal control characters. Raw paths must be direct canonical Markdown paths;
raw reads do not follow unsafe canonical symlinks or normalize obsolete schemas.
Malformed target documents can be repaired in an ordinary text editor. Unrelated
identifiable nodes remain editable when the current-format manifesto header is known.
For existing native forms, bounded identifiable repair fields preserve actual empty
body/partial source input separately from canonical graph membership. Native editing
can repair that input without substituting earlier text or pretending it parsed.

## Give an agent the relevant evidence

```sh
specspec diff --with-context
specspec diff <before-revision> --with-context --json
specspec diff --with-context --node <child-id> --node <another-id>
```

Full diff always retains complete canonical-file patches, including frontmatter,
comments, whitespace and line endings. Context adds deduplicated before/current
bindings, surviving parents and ancestor context, structural findings and finite
cause paths from both revisions. Repeated `--node` focuses the evidence packet.
`--max-bytes N` bounds the actual encoded result and fails before emitting a partial
successful response. Shared context is printed once per identity/version.

A retained declaration that becomes unresolved is different from a parent reference
actually edited out of a surviving file. Diff compares declared references rather
than silently dropping missing endpoints. A malformed file is unavailable material,
not proof that its node was deleted. Without Git, contextual diff retains current
bindings and explicitly labeled empty-inventory patches with a nonzero incomplete
result; it does not invent observed owner additions or prior justification.
Comparison completeness and graph validity are independent: a missing-parent graph can still have a complete known inventory and
declaration comparison. Partial reads retain available evidence with nonzero status.

An unchanged conclusion does not establish that its whole text is wanted. A removed
file does not establish an individual deletion gesture or motive. Dropping a parent
reference does not prove semantic justification. The agent uses bindings, differences
and optional owner explanations to propose a deliberate resolution.

Existing local `spotlight add` messages can describe invalid comparisons, including
missing identities present in declared references. Git commit messages can record
durable removal reasons. Neither message mechanism becomes a canonical lifecycle
state, approval receipt or compulsory deletion explanation.

## Make explicit repairs

```sh
specspec update <child-id> --parent <surviving-parent-id> --body revised.md
specspec update <other-id> --parent <parent-id> --require-valid
specspec check --warnings-as-errors
```

Normal add/update/delete permits graph-invalid intermediate results. Target document
schema, full identities, source-reference grammar, filesystem safety and transaction
checks remain enforced. Each successful mutation reports `applied`, `graph_valid`,
analysis completeness and diagnostics. A graph-invalid save completes its journal
normally; it is not an interrupted transaction.

`--require-valid` accepts an invalid starting graph but checks the **whole final
candidate before writing anything**. It applies to add/update/delete and batch apply.
It is useful at the end of a repair, not an approval gate on individual conclusions.
Use hidden integration `--parents-json '[]'` to explicitly replace a parent list with
an empty transitional list; repeated public `--parent` replaces a nonempty list.

Resolution may rewrite a conclusion around surviving justification, split it,
deliberately relink it, explicitly delete it, or recover a mistakenly deleted file
using ordinary Git tooling. The CLI never chooses those semantic outcomes for you.

## Apply one coherent multi-node change

```sh
specspec apply repair.json --dry-run
specspec apply repair.json --require-valid
```

The plan is a bounded JSON object with 1–1024 explicit edits. For example, replacing
schematic IDs below with actual complete IDs:

```json
{
  "edits": [
    {"op": "update", "id": "<C-id>", "parents": ["<B-id>"], "body_file": "c.md"},
    {"op": "add", "as": "part", "parents": ["<B-id>"], "body": "# Independent part\n"},
    {"op": "update", "id": "<D-id>", "parents": ["$part"]},
    {"op": "delete", "ids": ["<E-id>"]}
  ]
}
```

- `add` accepts body, parents, optional requirement/implementation type, sources and
  a unique local `as` name. `$name` references any new node in the same batch.
- `update` names an existing identifiable node and explicit replacement body,
  parents and/or sources. `delete` names exactly the files to remove.
- Body input is inline `body` or `body_file`, not both. Relative files resolve from
  the plan directory; `apply -` reads JSON stdin and uses the launch directory.
  Nested stdin body files are not accepted.
- Aliases never enter node files. Dry-run generated IDs are not reservations.
  Creation avoids existing names and declared parent identities, including dangling
  ones, so a random ID cannot accidentally supply a missing justification.
- Conflicting edits, duplicate JSON fields, unknown fields and malformed targets
  fail without writes. Plans and aggregate bodies are bounded at 16 MiB; individual
  node documents retain their 1 MiB limit.
- `--dry-run` has no canonical writes. Applying re-reads actual current files; a dry
  run is evidence, not a frozen workspace or a promise about later random IDs.
- Selected uncommitted deletions require normal consent (`--yes` noninteractively).
  The entire candidate is applied as one recoverable, byte-checked transaction.

## Exit codes and safety

Exit 0 means the requested operation/read was delivered, not that the graph is valid.
Structural error diagnostics can accompany `ok: true` after a saved intermediate edit.
Inspect `graph_valid`/snapshot validity, or run `check`, before treating repair as done.
Exit 1 means failed validation or a rejected/unavailable requested result; exit 2 means
invocation/I/O failure. An incomplete comparison can carry useful `result` evidence
with `ok: false` and nonzero status. Callers must not discard it automatically.

Locks, path/symlink protections, input bounds, original-byte checks and authorization
are independent of graph validity. If interrupted, retain `.specspec-local` and run
`recover`. Recovery restores only recognized original bytes, including an invalid
original graph; it refuses to overwrite new external text. A successful recovery can
therefore still report `graph_valid: false`. It is transaction recovery, not semantic
repair. No command implicitly stages, commits, installs hooks or deletes linked code.

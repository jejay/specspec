# Immediate justification and shortcut freedom

Canonical **node format 6** records a rooted, shortcut-free DAG. A direct parent
adds ancestry beyond the other direct parents: none of a node's direct parents
may already be an indirect parent. Parent depth can differ; the graph is not a tree.

```text
A → B → C       valid
A → B → C
└──────→ C      redundant A → C
```

Ancestor bindings carry justification. An implementation contributes its stated
realization toward those intentions; several implementations can jointly realize
an ancestor. Graph validity does not establish semantic fulfillment.

Changing a parent chain can change downstream justifications. Inspect both previous
and resulting impact; deliberately restore any independently needed relationship.
Removing current shortcuts preserves ancestor/descendant sets and longest paths,
but can change shortest distances, distance colors and immediate neighborhoods.

## One validation authority

The backend graph validator checks the complete graph after references, parent
types, root rules and acyclicity are sound. `REDUNDANT_PARENT` identifies the affected
node, direct edge and a deterministic alternative path. It never edits relationships.

- Managed `add`, `update` and other writes check the whole candidate before writing.
  An edit can make another node's edge redundant; rejected changes preserve files.
- `check` examines saved files. Native overlays and historical reads use the same
  graph rule. Native text can remain temporarily invalid and repairable.
- Owner-configured hooks and CI run `specspec check --staged` (optionally `--sources`)
  against exact index bytes. A repaired working tree does not mask a bad index.

`update --parent` still replaces one node's complete parent set. For a relationship
change involving several files, prepare the coherent Markdown changes together and
validate the full result before staging the complete intended graph. Managed writes
require a valid starting graph; repair invalid saved Markdown directly before using
them. There is no automatic repair, separate approval status or extra hook policy.

## Current-only contract and history

The current node format is **6**, with application API **6**. Fields, five-byte padded
Base64url IDs and source-region grammar retain their contracts. Older node formats
receive version diagnostics; there is no legacy reader or permanent migration command.
The upgrade requires deliberate, complete graph cleanup rather than silent read-time
normalization. Immutable spotlights retain original bytes; metadata cleanup can make
those captured versions resolve as changed against the current graph.

The maintained Gantt bundle, all retained revisions, original/deleted nodes, actual
CLI receipts and commit ledger use this same current rule. Use a fresh external
checkout for comparisons; existing manual clones and unrelated SpecSpec development
history remain untouched. See [the history procedure](../example/gantt/history/WALKTHROUGH.md).

## Verification

The maintained graphs contain 186 nodes/328 edges (SpecSpec) and 22 nodes/35 edges
(Gantt), with zero shortcuts. The 773 tests comprise 478 Python, 240 shared UI,
46 VS Code adapter and 9 Electron cases. Backend, renderer and host-adapter suites
cover independent closure/last-occurrence/selected-parent query oracles, default
compact/human bodies and source lists, comma-separated parents, worded hints/root
alignment, rooted metric frontier/path/closure oracles, union quotas and source
evidence boundaries, contract-aware source cues,
batched/lazy source equivalence, per-call freshness/process counts, controlled
polling/discovery/disposal lifecycles, complete node/edge readings,
deep/exponentially shared graphs, remote-redundancy atomicity, native repair,
an owner-configured hook in a disposable repository and exact-index/revision checks.
Gantt verification checks all eight retained commits, 123 actual CLI receipt states,
source retention and all three runnable model stages.

The [complete installed-host suites](investigations/host-smoke.md) exercise real
historical source previews, all eight color modes, three Spotlight backchannel
contexts, cascade HEAD/stage/commit ghosts and watcher-only invalid-file recovery.
Both complete Windows suites pass twice in succession.
Electron checks actual save, persisted draft/complete-list reload and revision
switching. VS Code checks native documents, split views, repair and CRLF/Unicode.
Canvas probes include six-theme overview fills, floating controls, rectangle capture
and unchanged native editing/world geometry. Mac gesture mapping has synthetic tests.

Controlled regressions hold background reads open while resolving sources, bind
previews to the published render/commit, replace pending requests and close projects
mid-read. Per-project bounded API channels reuse interpreter lifetime while each
request validates current files and Git state. HEAD/ref notifications, canonical
text changes and Spotlight arrivals use their respective coalesced paths. The
individual operation deadlines and complete-suite aggregate guards stay in force.
Tests preserve manual workspaces and install no repository hooks.

# One editing vocabulary and one invocation boundary

[Owner intention](../../.specspec/pRK4Qwk=.md) combines individual and multi-node
editing through add/update/delete. The [grammar choice](../../.specspec/4626uI8=.md)
keeps literal message input and existing host communication while turning composed
editing steps into one explicit final candidate. See the [CLI guide](../cli.md#compose-editing-commands)
and [invalid-state repair](../invalid-graphs.md#one-coherent-multi-node-change).

## Grammar and execution

- Only top-level add/update/delete can repeat or combine. Source, spotlight, reads,
  init, recovery and the application API retain standalone meanings. Their own
  argument values can still contain ordinary words such as `add`.
- `edit_cli.py` uses the declared Click option spellings/arities to identify step
  boundaries without splitting literal message/option values. Every step gets its
  normal Click parse before callbacks can read bodies or write files. Option choices,
  extra arguments and mixed non-editing commands fail without earlier-step effects.
- `add --as NAME` declares a short local alias. Quoted `$NAME` parent references can
  point forward or backward. New nodes get their fields in their add step; updates
  and deletions target existing nodes. The invocation describes one candidate, not
  sequential intermediate commits. Duplicate target edits, aliases and unresolved
  aliases fail without canonical writes. Neither aliases nor dry-run reservations
  enter node metadata.
- `--dry-run`, `--require-valid`, `--yes` and `--json` are invocation-wide wherever
  supplied. There is one result and at most one deletion confirmation. The complete
  final graph is the optional validity boundary; surrounding invalidity remains
  inspectable and editable.
- The existing `batch.py` domain planner allocates collision-safe IDs under the
  writer lock, resolves parent aliases and constructs explicit bytes/null deletions.
  `workspace.mutate` retains original-byte checks, journal recovery and path/schema
  protections. Recovery can roll back a mixed creation/deletion/update, including
  restoring an originally invalid graph. This is recoverable multi-file writing,
  not atomic cross-file visibility or a power-loss-proof database transaction.
- Default human output identifies generated aliases; JSON keeps `result.aliases`.
  Legacy ordinary singleton edit envelopes and deletion previews retain their shape.
  Single add/update previews and single named adds use the same candidate planner.

## Retained interfaces and limits

The separate `apply` command and its inline/file/stdin JSON batch-plan inputs are
removed, not hidden aliases. The domain's internal prepared-edit representation is
an implementation detail, not another command/input mode.

Hidden per-step `--body FILE|-` inputs remain for large UTF-8 bodies, with file paths
relative to the launch directory and at most one stdin body per invocation. Message/
body conflicts across all steps are rejected before any body reads. Hidden parent/
source inputs retain their prior roles. A reviewed deletion plan binds a standalone
delete: a chain rejects it before reading its input rather than discarding consent
evidence. Managed UI saves, reviewed deletion stdin, API-7 one-shot/stream channels
and native VS Code document persistence retain their existing interfaces and owners.
No host product code or protocol/schema cutover is needed.

Chains have at most 1024 steps, arguments and aggregate body material are separately
bounded at 16 MiB, and canonical nodes stay bounded at 1 MiB. Operating-system/shell
argv limits may be much smaller and can reject an invocation before SpecSpec starts.
Body files avoid placing large body text in argv; repeated flags do not bypass
aggregate OS limits. There is no automatic truncation, splitting, fallback or replay.
The [argument transport investigation](argument-authoring.md) records Windows bounds
and prior literal Unicode/CRLF probes. Bash examples quote `$name` to prevent shell
expansion. Other shells require their own native-argument quoting.

## Verification scope

Focused regressions exercise the owner's delete/add/add/update shape, forward
aliases, coparents, invocation-wide controls, exact bytes, command/flag-like literal
values, ordinary Click option completion, source-field association, syntax rejection before
input reads, selected deletion consent/cancellation, singleton compatibility, body
files/stdin, UTF-8 and incremental aggregate limits, invalid final candidates and
journal recovery of mixed additions/deletions/updates. Real Windows subprocesses exercise chained
Unicode/CRLF argv with ASCII/cp1252 output configurations. Existing transaction and
invalid-graph tests remain evidence for the shared writer, not semantic proof.

The final Python run passes **673 tests** after tightening aggregate body charging
so an oversized file chain stops before reading further inputs. The regression also
checks that over-budget literal bodies prevent opening any body files. Ruff/format
and whitespace checks pass. Shared UI passes 254 tests, VS Code 46 and Electron nine.

Complete installed Windows Electron and VS Code suites pass with actual managed
saves, reviewed deletion/repair, native dirty/Save/undo/redo/split/raw editing,
invalid-buffer repair, Unicode/CRLF, sources/spotlights/watchers and revision/reload
behavior. Shared UI phases took approximately 197 and 217 seconds respectively;
these are local observations, not production performance guarantees. The full host
runs preceded the final chain-only aggregate-loading guard; the complete Python
suite was rerun afterwards. UI single-edit execution paths and transports are
unchanged by that follow-up. An actual Git Bash delete/add/add/update invocation
also passed with quoted parent aliases, coparents and Unicode text. Physical
Linux/macOS and every PowerShell/cmd quoting variant are not qualified by these runs.

Every retained Gantt revision/ref was reconstructed externally through 123 actual
current-interface CLI executions, preserving all IDs, app bytes, redirects and
spec-before-code checkpoints. Its unchanged 45 literal-body authoring inputs remain
ordinary single steps; updated guides also describe composition. Every retained ref
and all three runnable model stages validate with current tools. The bundle and
ledger are refreshed together; the retained verifier/source anchors, receipts and
canonical snapshot remain byte-identical where no content changes are needed.

Exact-index graph/source checks are recorded with the final commit. Local logs,
review reports and external reconstruction paths remain under
`.specspec-local/edit-chains/`, including `python-final.log`, the three npm
`*-final.log` files, `electron-host.log`, `vscode-host.log`, `history-rebuild.log`
and `bash-probe.json`. Existing manual clones, earlier evidence and unrelated
SpecSpec history remain preserved. This change publishes no release and installs
no owner hooks.

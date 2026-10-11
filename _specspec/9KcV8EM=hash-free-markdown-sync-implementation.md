---
id: 9KcV8EM=
type: implementation
parents:
- tvic3PQ=
- 6SyZ-BU=
- LvYBN_4=
sources:
- path: src/specspec/model.py
  symbol: hash-free SpecNode records
- path: src/specspec/format.py
  symbol: parse_node, serialize
- path: src/specspec/workspace.py
  symbol: new_node, initialize, mutate, add_node, recover
- path: src/specspec/cli.py
  symbol: API 3 and removed expectation options
- path: src/specspec/git.py
  symbol: direct semantic/byte comparisons
- path: graph-ui-common/host/session.cjs
  symbol: GraphSession refresh, configurePolling, handle
- path: graph-ui-common/host/watch.cjs
  symbol: GraphWatcher
- path: graph-ui-common/media/graph-model.js
  symbol: sameNode, renderMatches
- path: graph-ui-common/media/graph.js
  symbol: original node draft and sync-error handling
- path: vscode/src/extension.ts
  symbol: directory/file watcher and polling setting lifecycle
- path: vscode/package.json
  symbol: specspec.pollIntervalMs default 0
- path: electron/main.cjs
  symbol: GraphWatcher and trusted polling launch setting
- path: tests/test_markdown.py
- path: tests/test_ids.py
  symbol: canonical IDs, current-only validation and collision retry
- path: graph-ui-common/test/session.test.cjs
- path: graph-ui-common/test/watch.test.cjs
- path: graph-ui-common/test/graph.test.cjs
- path: vscode/test/extension.test.cjs
- path: graph-ui-common/test-host/platform.cjs
  symbol: real manual/invalid-file synchronization without polling
- path: example/gantt/history/verify.py
  symbol: current receipts and independent compliant Git bundle
- path: .github/workflows/ci.yml
  symbol: shared/adapters watcher tests on Windows, Linux and macOS
- path: graph-ui-common/view.cjs
  symbol: persistent sync-notice
- path: graph-ui-common/media/graph.css
  symbol: out-of-date banner
- path: graph-ui-common/test/graph-model.test.cjs
  symbol: sameNode and full membership without hashes
- path: graph-ui-common/test-host/ui.cjs
  symbol: foreground test window and transition completion wait
- path: vscode/test-host/run.cjs
  symbol: installed Windows VS Code recheck
- path: vscode/test-host/smoke.cjs
  symbol: real complete-render acknowledgement
---
## Current compact-ID and history correction

The implementation/verification below records earlier revisions. Its legacy-reader,
schema-migration, original API-2 receipt and root-history compatibility descriptions
are superseded by qowy5AI= and YaXJpGE=. Current production code supports only the
canonical Base64url node scheme, with no old-schema reader or migration command.
The default node-editor association is **/_specspec/???????=*.md. Gantt's maintained
history is rewritten and bundled; tests do not require old root graph revisions.
Earlier run counts are historical evidence, not claims about this revision. The
separate current implementation record documents the new checks and limitations.

# Implement hash-free files, watcher refresh and optional default-off polling

The Python model/CLI/writer and both shared UI hosts remove content hashes,
fingerprints and --expect. Current files/API use version 3; old v1/v2 revisions
remain readable without marker checks and migrate through one recoverable batch.
Both working graphs were migrated through the CLI. Schema/DAG/authorization,
original-byte transaction checks, exact-index validation and recovery remain.

GraphSession serializes/coalesces reload hints, retries incomplete reads twice,
compares loaded records directly to skip unchanged redraws and offers an optional
millisecond polling timer defaulting off. VS Code's resource-scoped pollIntervalMs
setting updates live. Electron uses --poll-interval-ms/SPECSPEC_POLL_INTERVAL_MS from
trusted launch settings, not project/renderer data. Its directory/parent GraphWatcher
reattaches on replacement/recreation, reports errors and never turns on fallback
polling. Closure/project switches stop old watchers/timers. Historical targets stay
read-only and ignore workspace refresh hints.

Drafts keep original node records, not hashes. Watcher updates preserve DOM/caret,
camera and text; same-node overwrite requires confirmation, unrelated edits do not.
Missing original legacy drafts require overwrite confirmation rather than silently
inventing a baseline. Deleted nodes retain visible copyable drafts, not recreation.
Invalid reloads keep the last valid graph clearly marked out of date and disable
mutations until fixed; external files are never repaired or overwritten on reads.
UI writes re-read current files. Sequence tokens/full membership still check rendering.

Verification: 77 Python tests, 85 shared tests, 29 VS Code adapter tests, 9 desktop
unit tests, Ruff and the original three-stage Gantt history verifier passed locally.
Shared tests exercise real Windows watcher saves/atomic replacement/deletion/directory
recreation plus injected errors, polling/disposal/coalescing, transient/invalid data,
authorization/history, overwrite cancellation and exact native draft preservation.
CI is configured for shared/editor tests on Windows/Linux/macOS; remote execution
is not claimed. Real-host checks are recorded after their final run, not presumed
from unit results. Watchers are filesystem-dependent hints; arbitrary editors can
race final replacement, and no universal event delivery or power-loss guarantee
is claimed. No automatic staging/committing, hook installation, installer or release
is introduced; Git commits require the user's explicit authorization.


## Final local verification boundary

All 77 Python, 85 shared, 29 VS Code adapter and 9 desktop unit tests pass, as do
Ruff check/format, both warnings-as-errors graph validators and the independent
example's original three-stage history audit. The Windows Electron real-host suite
passed on a disposable 69-node working/70-node display fixture: watcher-only manual
and invalid-file updates, no external-file rewrite, native draft/caret preservation,
valid-file recovery, actual UI save, external-change draft reload, revision/history
switching, full geometry/camera/hover/paint checks and sandbox/network boundaries.
Native overwrite confirmation is tested through the shared session, not silently
auto-accepted by the real-host harness. A persistent out-of-date banner survives
navigation/notices while invalid files disable mutations. API-3 acknowledgements
require visible membership, not old count-only reports or hashes.

The camera smoke helper now brings its own test window forward and waits for the
actual 100% transition before synthetic panning, avoiding background-frame timing
failures without changing the production camera. The initial installed VS Code
smoke attempts were blocked by an update in progress. On the user's requested
recheck, all 29 adapter tests and the real Windows VS Code suite now pass on the
same disposable 69-node working/70-node display fixture: complete rendering,
watcher-only manual/invalid-file sync, draft/caret preservation, valid-file recovery,
geometry/camera/hover/paint and native controls. Deliberately invalid test files are
restored; both actual repository graphs pass warnings-as-errors validation without
repairs. This is no longer an unverified VS Code host claim for this revision.

CI is configured for shared/editor tests on Windows/Linux/macOS, but macOS/Linux
and remote CI runs remain unclaimed. Older package evidence remains historical.
The user explicitly authorized committing the complete graph/backend/UI change
and its existing Electron launch-path dependency after this recheck; local settings
and original artwork stay outside that commit. Both root and nested exact-index
snapshots must be checked after staging, not substituted by working-tree validation.

# Installed-host verification

Run the complete installed applications against disposable clones of the maintained
Gantt history:

```sh
npm --prefix vscode run test:host
npm --prefix electron run test:host
```

Each runner builds its host from the shared sources and uses an isolated profile.
Existing manual workspaces, settings, Git hooks and retained example experiments
stay under owner control.

## Complete Windows runs

Both complete suites pass in two successive runs of the current implementation:

| Host | Run 1 | Run 2 | Exit |
| --- | ---: | ---: | --- |
| VS Code | 218.63 s | 168.66 s | 0 / 0 |
| Electron | 167.23 s | 170.17 s | 0 / 0 |

Elapsed times include build and disposable-fixture setup. Both runs include each
host's final native or reload/revision phase. Core verification passes **565 tests**:
281 Python, 231 shared UI, 44 VS Code adapter and 9 Electron. Ruff, root/Gantt source
checks and every maintained history revision/receipt also pass.

## End-to-end coverage

Both suites exercise:

- Literal historical/working source previews and independent revision context.
- Theme and Git paint, six-theme overview fills, floating controls, rectangle framing,
  real pointer capture/outside release and retained native editing selection.
- All eight fill modes, with independent raw-count/cohort/logarithmic calculations
  for the four influence choices and unchanged world/camera checks.
- Compact, circular-manifesto and expanded-card Spotlight backchannels, actual CLI
  publication/readback, exact-version highlights and retained arrival baselines.
- HEAD/stage/commit deletion ghosts, shared-descendant cascades, outside parents,
  uncommitted warnings and exact staged validation before fixture commits.
- Watcher-only external/invalid-file repair, retained drafts, original records and caret.

Electron additionally verifies sandbox/network restrictions, actual managed saves,
persisted draft and complete Spotlight-list reload, zero-arrival baseline, and
historical/workspace switching. VS Code additionally verifies default native file
editors, split views, Save/undo/redo, raw repair and CRLF/Unicode persistence.

## Responsive read scheduling

Source previews have an independently coalesced read-only lane, bound to the published
render and displayed commit. Navigation/newer requests invalidate obsolete replies;
mutation and native-plan serialization retain their owners. Graph-only refreshes
leave unchanged Spotlight metadata alone. Initial loading, explicit Refresh, configured
polling and independent store events keep list delivery current.

Both hosts share asynchronous HEAD/ref watching. Discovery coalesces requests and
retries within its bounded operation allowance. Index stat-cache and Git-extension
status churn leave the HEAD-to-working presentation unchanged; canonical files have
their own watchers. Staged source operations read the actual index on invocation.
Successful HEAD reads resolve directly, with unborn-branch checks on unresolved HEAD.

Regressions hold graph and metadata reads open while delivering a source preview,
replace pending preview requests, move comparisons, dispose in-flight work and drive
Git-discovery failures/recovery. These are controlled causal checks rather than
throughput assertions tied to a fast machine.

## Execution settings

Disposable Chromium hosts use reduced motion for reproducible pose sampling and
disable background/renderer/occlusion timer throttling. Production camera behavior
retains its normal-motion tests. CDP disconnects reject pending operations promptly.
The shared UI allowance is 300 seconds, native lifecycle 160 seconds, startup/shutdown
40 seconds and Electron reload/revisions 60 seconds. Aggregate guards remain
400 seconds for Electron and 500 seconds for VS Code. Individual operation deadlines
and all substantive assertions remain in force.

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

Both complete suites pass with metadata-only comparison spotlights:

| Host | Complete run | Exit |
| --- | ---: | ---: |
| VS Code | 61 s | 0 |
| Electron | 53 s | 0 |

Elapsed wall times include build and disposable-fixture setup; the hosts ran
concurrently. Each includes its final native or reload/revision phase. Core
verification passes **570 tests**: 277 Python, 240 shared UI, 44 VS Code adapter
and 9 Electron. Ruff and working source checks pass. Maintained Gantt history and
receipts retain current-schema validation; the local spotlight format change does
not change canonical node format/API 6.

## End-to-end coverage

Both suites exercise:

- Literal historical/working source previews and independent revision context.
- Theme and Git paint, six-theme overview fills, floating controls, rectangle framing,
  real pointer capture/outside release and retained native editing selection.
- All eight fill modes, with independent raw-count/cohort/logarithmic calculations
  for the four influence choices and unchanged world/camera checks.
- Compact, circular-manifesto and expanded-card Spotlight backchannels, actual CLI
  publication/readback, one-white-ink identity highlights and retained arrival baselines.
- Metadata-only spotlight selection across real stage/02-code → stage/03-spec
  comparisons, with added/deleted rings and a retained unsaved form draft.
- Live workspace changes produce visible drift warnings in both UI and CLI while
  the changed node remains highlighted; reverting the node clears the warning.
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
The installed paint oracle independently checks the current 40%-to-16% fill
schedule. Spotlight probes await the comparison/application round trip before
sampling rings, and derive ring widths from the camera-scaled CSS properties.
Reload checks include all 23 retained records from the backchannel, drift and
historical-comparison scenarios.

The shared UI allowance is 300 seconds, native lifecycle 160 seconds, startup/shutdown
40 seconds and Electron reload/revisions 60 seconds. Aggregate guards remain
400 seconds for Electron and 500 seconds for VS Code. Individual operation deadlines
and all substantive assertions remain in force.

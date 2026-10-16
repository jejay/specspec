# Windows installed-host smoke investigation

The complete installed Electron and VS Code suites pass on the unattended Windows
laptop. These are local, disposable-profile runs, not Linux/macOS or remote-client
qualification. The local environment uses Python 3.14.5 and Node 24.21.0.
Production operation deadlines, renderer geometry and default-off
polling remain unchanged.

## Findings and changes

1. **The Electron cascade stall was an aggregate watchdog expiry.** Its runner
   killed the app at 180 seconds during the expanded shared UI workload. The pending
   CDP evaluation subsequently timed out, making the failure look like a stuck
   cascade renderer. Running the entire suite with only that aggregate guard
   extended reached the final success marker, including persisted draft/spotlight
   reload and historical/workspace switching. A cascade-only diagnostic also
   completed the full HEAD/stage/commit lifecycle.
2. **VS Code's UI phase outgrew its 160-second guard.** A traced sequential run
   passed the source preview and all three backchannel contexts, then the guard
   terminated it during deletion checks. The full measured UI phase is about
   254 seconds on this machine. Native lifecycle retains its 160-second allowance.
3. **Supersession is not invalid Markdown.** Watcher/generation changes during
   valid reads can exhaust three attempts while shots or Git changes arrive.
   `ProjectReads` now raises a distinct `SupersededReadError`; `GraphSession`
   discards that result and coalesces a fresh automatic attempt while preserving
   the existing presentation. Explicit working refreshes report retry and schedule
   a follow-up. Actual schema/read failures still mark the last-valid graph and
   restrict actions; mutation preflights remain fresh. Closing a project is distinct
   from supersession and disposal cancels pending work.
4. **Optional window sizing must not gate foregrounding.** Electron can reject
   `Browser.getWindowForTarget`. The harness now independently attempts
   `Page.bringToFront`. Both disposable hosts disable background/occlusion timer
   throttling. VS Code needs explicit `=true` on these otherwise unknown switches:
   a bare final switch consumes the following workspace path and opens an empty
   window. A regression assertion protects the launch arguments.
5. **Transport closure should not become a fictitious request timeout.** The shared
   CDP client rejects readiness and pending calls promptly on close/error and clears
   their timers. Aggregate expiry is logged explicitly. Protocol errors, JavaScript
   exceptions and individual request timeouts remain failures.
6. **Click help must also survive legacy Windows pipes.** `diff --help` emitted a
   Unicode arrow through cp1252 text stdout and crashed before normal guarded output.
   Static root/diff help now uses ASCII punctuation. Four real subprocess cases
   force ASCII/cp1252; readable results, diagnostics, JSON and canonical text retain
   their existing explicit UTF-8 byte handling. Repository instructions use the
   current `show`, `check`, positional `diff BASE` and exact-index command spellings.
7. **Binding-text guards distinguish runtime states from design history.** A broad
   word ban mistook the current term “superseded read” for a withdrawn specification.
   The repository check retains historical-language/retired-section safeguards while
   permitting that runtime term. A regression case checks current read handling and
   rejects retired-design sections through the shared binding guard.
8. **A passing run missed a randomly invalid fixture commit.** A later confirmation
   selected the uncommitted setup addition as its second outside parent. Only the
   cascade files were staged, so its resulting HEAD referenced a missing parent;
   the UI correctly reported an unavailable comparison and could not display the
   expected ghosts. Selection now requires live HEAD membership, and the fixture's
   Git wrapper checks the complete exact index before every commit. A deterministic
   regression puts an uncommitted root child first. The failed profile/independent
   repository remain retained as evidence; the maintained Gantt bundle is valid.

The earlier VS Code pending-source-preview assertion did not reproduce in the
traced sequential run or the complete corrected run. Foreground/occlusion handling
and avoiding false-invalid retry states improve the surrounding conditions; this
is not evidence for one uniquely established cause of every prior source-preview
failure. Its existing individual assertion deadline is unchanged.

## Bounded test allowances

`graph-ui-common/test-host/budgets.cjs` is the single test-budget source:

| Allowance | Milliseconds |
| --- | ---: |
| Shared UI phase | 300,000 |
| Native lifecycle phase | 160,000 |
| Startup/shutdown reserve | 40,000 |
| Electron reload/revision reserve | 60,000 |
| Electron outer guard | 400,000 |
| VS Code outer guard | 500,000 |

Outer guards cover the sum of their phases. These are aggregate test ceilings,
not per-operation or product performance guarantees. CDP, source, pose, watcher,
form, native request and production CLI deadlines retain their prior values.

## Complete-run evidence

Run the installed suites sequentially on a shared laptop so competing windows and
process startup do not confound diagnosis:

```sh
npm --prefix electron run test:host
npm --prefix vscode run test:host
```

| Installed Windows run | Result | Wall time including build/fixture |
| --- | --- | ---: |
| Electron | `SPECSPEC_ELECTRON_HOST_OK` | 264 seconds |
| VS Code | `SPECSPEC_REAL_HOST_SMOKE_OK` | 409 seconds |

These confirmations include the corrected fixture and its exact-index checks.
The shared UI phases report 227,072 ms and 269,834 ms respectively. Both exercise
actual source previews, compact/circular/expanded backchannels with external CLI
readback, and descendant cascade ghosts through staging/commit. They also check
manual/invalid-file synchronization and draft/caret preservation. The deliberate
invalid-file fixture emits schema diagnostics before successful repair; that is
expected negative-path coverage, not an unexpected suite failure.

Electron additionally checks sandbox/blocked network, actual managed Save, stale
input retention, complete 21-shot list reload with a zero-arrival baseline, retained
draft reload and historical/workspace switching. VS Code additionally checks the
default custom editor, native dirty/Save/undo/redo, split synchronization, independent
cameras, raw edits, invalid-buffer repair, and different-node CRLF/Unicode saves.

Local diagnostic logs and failed profiles are retained under
`.specspec-local/smoke-debug/` and the printed temporary-profile paths. VS Code smoke
opts into loading diagnostics only inside its disposable profile. Tests do not
change real user settings, install repository hooks, reset manual clones or require
UAC elevation. Actual macOS Command+Shift, Linux desktop and remote transport runs
remain separately scoped evidence.

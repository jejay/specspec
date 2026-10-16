# Windows installed-host smoke investigation

The `c2a93b4` baseline's complete installed Electron and VS Code suites passed on
the unattended Windows laptop. The influence-mode follow-ups below separate
successful feature probes from later full-suite failures and verification limits. These are local, disposable-profile runs, not Linux/macOS or remote-client
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

## Complete-run evidence for the c2a93b4 baseline

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

## Influence-mode follow-up

Both installed hosts pass the Absolute influence and Relative influence probes:
independent full-revision descendant traversals and longest-path cohorts agree
with every compact card's accent, the continuous gradient is actually painted,
preferences persist, and the world positions/camera remain unchanged. The current
full VS Code suite exits zero in 458.39 seconds, including its native lifecycle.
Its shared UI phase reports 312,159 ms. Electron's full shared UI phase succeeds
in 362,237 ms, including both new modes, all backchannels, cascade ghosts and
invalid-file recovery. Persisted draft/21-shot reload and the zero-arrival baseline
also pass before the subsequent comparison-dialog assertion.

The full Electron rerun exits one at the existing `Compare revisions` dialog-open
assertion following a fixed 200 ms wait. Its current full-suite success is therefore
unconfirmed. These observations do not establish the unique cause of that later
failure. No aggregate or individual deadlines were changed for the new modes.
Logs, retained diagnostic profile/repository paths and serial-run exit/timing data
are in `.specspec-local/influence/`.

The linear-only follow-up completed 273 Python, 191 shared UI, 42 VS Code adapter
and 9 Electron tests; the full Gantt history/receipts/source verification also passed.
Two earlier foreground command attempts were interrupted by their tool-level
allowances at different Python-test positions; a closed-stdin diagnostic run then
completed all 273 tests in 163.29 seconds. No unique cause of those interruptions
was established, and they are not counted as completed runs.

## Permanent linear and logarithmic influence

All four influence choices are part of the specification. Linear and logarithmic
modes share raw unique-descendant ranges, revision-local longest-path cohorts and
the same continuous warm palette. Logarithmic normalization transforms raw counts
with `log1p` before subtracting the transformed minimum. Tests cover positive cohort
minima, zero/tied groups, generated closure oracles, independent base/target context,
all four preferences and preservation of form/caret/camera/world state.

That influence follow-up completed 273 Python, 193 shared UI, 42 VS Code adapter and
9 Electron tests, Ruff lint/format, both saved source/graph checks and the full
Gantt history/receipt/source verification. Both installed Windows hosts pass each
of the four explicit influence probes: expected accents from independent graph and
scaling calculations, actual gradient paint, selection persistence and unchanged
world/camera. Their logs name each passed mode separately.

That influence follow-up's broader installed-suite results were bounded:

| Run | Result beyond the four passed influence probes |
| --- | --- |
| Electron, 420.66 s including build/fixture | The existing 400,000 ms aggregate watchdog ends the run after watcher/invalid-file recovery, before final reload/revision qualification. |
| VS Code, 231.33 s including build/fixture | A later expanded-manifesto Spotlight backchannel check finds a changed camera pose, after all four influence probes passed. |

The VS Code camera assertion is at `checkSpotlight`, not the influence-mode
world/camera assertions. No unique cause of that later pose change was established;
the all-eight-mode installed/native/reload qualification is not claimed complete.
The Electron comparison check now polls its actual asynchronous dialog-open state
using the adjacent reload checks' 30-second readiness allowance instead of a fixed
200 ms pause. That watchdog-ended run did not confirm the later check.
No aggregate guards, production deadlines or other individual test limits were
increased. Preserved current logs, exit records and failed profile/repository paths
are in `.specspec-local/influence/permanent/`.

## Zoom-aware canvas and rectangle framing

The specification plan is commit `58b6b6b`. Separate intentions cover solid overview
node shapes, concise positive copy, floating icon controls and one-shot rectangle
framing. The interpolation and pointer-capture choices retain native forms, world
layout, Git/highlight roles and all four influence modes.

The completed core checks pass 273 Python, 207 shared UI, 42 VS Code adapter and
9 Electron tests (**531 total**), Ruff lint/format, both source/graph checks and
maintained Gantt history verification. The shared camera suite covers inversion,
every drag direction, modifier release before/during a drag, one-shot completion,
Escape from the focused tool button, cancelled-release click consumption, native
controls, pointer identity, capture loss, blur and disposal. Mac Command/Control
boundaries have synthetic coverage; physical macOS qualification remains separate.

Both installed Windows hosts pass the early canvas probes: actual/intermediate/
minimum fill interpolation in dark/light/contrast themes, explicit missing-border-
token cases, the hovered white manifesto endpoint, full-canvas floating controls,
modifier latching and real Chromium pointer capture with outside release. Intrinsic
world positions and native editing selection remain intact. Both also pass each
linear/log influence probe and the compact/circular/expanded Spotlight backchannels.

The rendering probes now restore actual size before checking the exact editing
tints, reframe before clipped hover checks and compare rendered RGBA colors instead
of browser-specific CSS serialization. A missing contrast-border token exposed an
invalid-color edge case; the fill/border rule now falls back to host foreground.
The invalid-file watcher probe checks the concise repair status, visible last-valid
notice and disabled Save together. Its former text predicate waited for wording
replaced by this UI revision. All substantive repair assertions remain.

A polling unit assertion depended on how many reads fit into 70 ms and failed in
both a whole-suite attempt and isolation. Its replacement holds an explicit read
barrier, drives repeated hints, verifies one in-flight comparison and exactly one
follow-up, then keeps the historical-target/annotation checks. Three isolated
barrier repetitions and the complete shared suite pass. Production polling and
operation/aggregate deadlines are unchanged. Logs and screenshots are preserved
under `.specspec-local/canvas-polish/`.

Final full-host attempts retain these qualification limits:

| Run | Completed scope and later boundary |
| --- | --- |
| Electron, 445.24 s including build/fixture | Canvas paint/framing, four influence modes, all three backchannels, cascade lifecycle and watcher/invalid-file recovery pass. The existing 400,000 ms aggregate guard ends the later save/reload work. |
| VS Code, 145.94 s including build/fixture | Canvas paint/framing and Git paint probes pass. A subsequent historical source preview remains at “Resolving source region…” when its existing wait ends. |

Earlier qualified runs also passed all four influence modes and all three
backchannels in both hosts before the stale invalid-file text predicate was found.
The final VS Code source-preview wait has no established unique cause; complete
installed/native/reload qualification is not claimed. The new canvas probes pass
in each retained attempt, including the explicit contrast-token fallback matrix.
The final `complete-*.log` files and `complete-hosts.json` retain actual exits and
failed profile/repository paths. No production or smoke deadlines were enlarged.

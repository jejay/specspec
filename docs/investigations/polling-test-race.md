# Polling shutdown: separate watcher events from timer ticks

## Causal reproduction

The VS Code test originally counted all CLI requests, switched polling off, waited
260 ms, then expected the count to stay fixed for another 30 ms. The fixture also
started the real asynchronous `GitWatcher`, including its initial Git subprocess.

Initial discovery calls the project's change handler when it finishes, including
for a non-Git folder. That is a valid watcher hint. The view then schedules a normal
200 ms debounced graph refresh. Polling zero stops periodic ticks; it intentionally
keeps filesystem/Git/Spotlight watching and explicit Refresh available.

A controlled execution of the real watcher reproduces the exact **6 versus 5**
assertion without relying on CPU contention or a real delay:

| Virtual time | Event |
| --- | --- |
| 0 ms | Graph open completes with 3 CLI calls; Git discovery is held pending |
| 10 ms | Poll performs graph/metadata reads; count becomes 5; polling is disabled |
| 80 ms | Initial discovery completes and schedules its watcher refresh for 280 ms |
| 270 ms | The old test's 260 ms wait ends; it saves count 5 |
| 300 ms | The watcher refresh has run; the old assertion sees count 6 |

The only new request in the final window is a graph `read`, caused by discovery,
not another interval tick. This establishes a concrete race in the test oracle;
the original intermittent run did not retain per-event tracing, so it cannot prove
that no other already-requested follow-up could also have hit that window.

## Correction

The VS Code fixture now exposes the actual sessions/watchers and can supply a
controlled Git executor to the real watcher. Default tests retain real Git behavior.
Polling-specific tests use virtual timeout/interval clocks and await the session's
queue, metadata work and completed view disposal rather than a wall-clock quiet
period. Configuration itself can legitimately trigger a graph refresh and is
settled explicitly before checking that no more periodic work arrives.

Causal regressions verify that:

- Polling defaults off; enable/disable and interval replacement control ticks.
- A late initial discovery still refreshes while polling is off.
- Subsequent filesystem hints still refresh while polling is off.
- Closing with discovery pending ignores its late result and starts no new reads.
- A blocked read coalesces pending requests into one follow-up after polling stops.
- Historical targets avoid graph polling while metadata recovery remains available.

The two shared-session polling tests also use virtual clocks and explicit read
gates. Existing real Git/filesystem watcher integration tests remain separate.
Product scheduling, debounce/retry intervals, operation deadlines, mutation/save
ownership and disposal behavior are unchanged. The fix neither suppresses legitimate
watcher updates nor extends sleeps to make the assertion less likely to fail.

## Original verification

Run the causal tests directly:

```sh
node --test --test-name-pattern="poll|initial Git discovery" \
  graph-ui-common/test/session.test.cjs vscode/test/extension.test.cjs
```

The VS Code adapter must be compiled first (`npm --prefix vscode run compile`).
The five causal tests pass 20 repetitions with two concurrent workers: 100 test
executions without wall-clock timing assertions. Full validation also passes
371 Python, 240 shared UI, 46 VS Code and 9 Electron cases, Ruff, working/exact-index
source checks and all eight retained Gantt revisions.

Complete shared, adapter and Electron suites retain their normal test commands.
The Node test runner's virtual timers are test-only; real watchers keep their own
bounded asynchronous integration coverage. No production or canonical schema/API
change is involved.

## Spotlight-only read-count follow-up

The 0.0.1 general CI run exposed the same independent event boundary in another
adapter test. It recorded graph reads after opening two views, created an external
Spotlight and expected no additional graph reads. Real startup Git discovery could
complete during that interval and correctly refresh one or both views. CI observed
5 versus 4; this did not establish that the Spotlight event caused a graph reload.

A retained controlled reproduction uses the original test, holds the real watcher's
Git executor pending until after its baseline, then completes it. The ordinary
200 ms watcher debounce produces the assertion failure (6 versus 4 locally) without
changing production code. The observed count depends on coalescing across the two
views; the causal independent hint is explicit rather than inferred from a rerun.

The Spotlight-specific test now holds that unrelated discovery pending until
teardown. It retains the strict unchanged graph-read count, real filesystem
Spotlight watching and notifications to every view. Existing controlled-clock
late-discovery tests still prove the real graph refresh/disposal behavior. The
correction adds no sleeps, longer deadlines or production event suppression.
[Release evidence](pypi-0.0.1.md) records the remote failure and final follow-up scope.

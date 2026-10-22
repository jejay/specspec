# A planning app that changes its mind

A runnable Gantt example with an independent `_specspec` graph and agent-planned
spec-before-code development through two substantial redirects. Every retained
graph describes that stage's current product positively, with separately reasoned
conclusions and actual implementation mappings. Git records changed decisions. The existing
[fictional story](STORY.md) is optional illustration, not required evidence or
actual authorization. The final graph has **22 nodes**; 22 earlier nodes were
physically deleted during redirects and remain in the earlier Git commits.
Every retained revision uses shortcut-free node format 7 and application API 6.
The final graph has 35 immediate justification edges; ancestry supplies inherited
bindings and changes require downstream reconsideration.

## Use the independent repository, not this tracked snapshot, for Git

`example/gantt` in the SpecSpec checkout is a tracked fixture snapshot. **Git in
this folder uses the surrounding development repository**, whose old schemas are
intentionally unsupported. This explains failed UI comparisons of its old commits.
Do not install nested `.git` metadata here or resurrect legacy schema readers.

The [complete Git bundle](history/gantt.bundle) holds a separate rewritten,
current-schema history. From the SpecSpec root, with development Python active:

```sh
python example/gantt/history/checkout.py
# Or choose a new external folder:
python example/gantt/history/checkout.py ../specspec-examples/gantt
```

Default: `~/Projects/specspec-examples/gantt` (Windows:
`~\Projects\specspec-examples\gantt`). Existing destinations are never overwritten.
Open **that clone** as the project in VS Code/Electron. From the clone:

```sh
git rev-parse --show-toplevel
python -m specspec check --warnings-as-errors
python -m specspec diff stage/01-code stage/02-spec
python -m specspec diff stage/02-code stage/03-spec
```

Use the same tags in **Compare Revisions**. The clone has its own Git root, index,
ancestry and worktree; it never depends on SpecSpec's obsolete historical schemas.
See the [history/maintenance walkthrough](history/WALKTHROUGH.md).

| Stage | Spec / code tags | Change |
| --- | --- | --- |
| 01 | `stage/01-spec` / `stage/01-code` | Portfolio, weekday forecasts, owners/rollups; cloud/leveling remain candidates |
| 02 | `stage/02-spec` / `stage/02-code` | Personal manual dates/weekends/priorities; **13/17 nodes deleted** |
| 03 | `stage/03-spec` / `stage/03-code` | Workshop durations/prerequisites/earliest bounds/baseline; **9/16 nodes deleted** |

Every spec checkpoint is an `Agent specspec changes:` commit and precedes its code.
The [agent guide](AGENTS.md) describes owner/tandem/agent/implementation phases.
This is an explicitly reconstructed fixture with existing canonical identities
reused at creation and new actual CLI outputs. Existing manual clones retain their
local experiments. Deleted branches retain their identity,
body, parents and sources in earlier commits, not flagged files in HEAD. Redirect
commit messages explain why; default workspace shows deleted HEAD nodes as D until
the deletion is committed, including after staging. `history/cli.jsonl` records actual reconstructed CLI executions;
`history/revisions.json` records actual fixture commits and receipt ordinals.
These are real executions in an intentionally synthetic history, not a claim that
untouched original commits used today's encoding. No approval workflow is involved.

**Whenever the node schema changes, rewrite the entire maintained example history
as if every revision had always used the current SpecSpec version.** Updating only
HEAD is insufficient. Refresh all refs, ledgers, receipts, snapshot and bundle;
validate every revision with current tools. The walkthrough gives the maintenance
procedure. Existing manual clones must be explicitly recreated after preserving
local work. Unrelated SpecSpec development history is never rewritten.

## Run the final app

From your independent clone, open `index.html`, or serve a stable local origin:

```sh
python -m http.server 8000 --bind 127.0.0.1
# Visit http://127.0.0.1:8000
```

Capture a baseline, select Prepare materials, change its duration from 3 to 6
workdays and save. The workshop finish moves from April 20 to April 21; the baseline
remains unchanged. Add/edit/remove tasks and prerequisites with native forms.
Cycles and deleting a referenced prerequisite preserve drafts. Export JSON or
preview `history/personal-v1.json`; conversion explains changed weekend/end-date
semantics and lost priorities before explicit Apply.

Forecasts use Monday–Friday workdays and optional earliest bounds. No holidays,
partial days, resource leveling, portfolios, accounts or synchronization. Finish
deltas count calendar days. Limits: 100 tasks, durations 1–60 workdays, dates
2000–2100, chart horizon 730 days. Baselines are snapshots, not approval.

Valid edits autosave locally. Corrupt/old application JSON stays protected until
explicit Apply/reset and can be downloaded. Storage denial is visible. Browser
storage is not durable backup or sync; file-origin support varies. There is no
runtime API, CDN, remote script or app build dependency. App JSON v1 conversion
is unrelated to obsolete SpecSpec node schemas.

## Explore and check

From the clone:

```sh
python -m specspec show
python -m specspec diff
python -m specspec query <full-id> --max-distance 0 --with-ancestors
npm test
npm run test:browser
```

IDs are canonical padded Base64url over five random bytes, including `=`; filenames
are `<id>.md`. Manual Markdown is permitted and validated; CLI/UI editing is
recommended. Do not reinitialize the graph. Node 22+ is needed for the installed
Chromium browser harness; no app dependencies or browser downloads are required.
`GANTT_BROWSER` selects the installed browser; `GANTT_SCREENSHOT_DIR` saves screenshots.
Tests use loopback and disposable profiles, not personal data.

From the SpecSpec checkout, verify the portable fixture independently:

```sh
python example/gantt/history/verify.py --history
python -m pytest tests/test_example_checkout.py tests/test_gantt_example.py tests/test_gantt_git.py
```

Tests/CI clone the bundle, not your manual workspace. Current snapshot/runtime/test
consistency is checked. Historical checks do not modify this checkout's index or
history. Existing Windows browser evidence is bounded prototype verification,
not exhaustive accessibility/platform/performance/security proof or a remote CI claim.

Before an authorized SpecSpec-checkout commit, validate both **exact staged** graphs
from its root: `python -m specspec check --staged` and
`python -m specspec --root example/gantt check --staged`. In an independent example
repository, only its own `check --staged` applies. No hooks are installed automatically.

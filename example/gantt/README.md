# A planning app that changes its mind

A runnable spec-aware Gantt example with a clearly [simulated user/AI dialogue](STORY.md),
two substantial redirects, a separate `_specspec/` graph and real spec-before-code
Git stages. Its **maintained history has been rebuilt with current SpecSpec tooling**.
The independent [Git bundle](history/gantt.bundle) is the rigorous versioning test
corpus, not the surrounding SpecSpec repository's evolving historical schemas.

## Run the final app

Open `index.html`, or use a stable local origin for predictable browser-local storage:

```sh
python -m http.server 8000 --bind 127.0.0.1 --directory example/gantt
# Visit http://127.0.0.1:8000
```

Capture a baseline, select Prepare materials, change its duration from 3 to 6
workdays and save. The workshop finish moves from April 20 to April 21; the baseline
remains unchanged. Add/edit/remove tasks and prerequisites with native forms.
Cycles and deleting a referenced prerequisite are rejected without losing drafts.
Export JSON or preview `history/personal-v1.json`; conversion explains changed
weekend/end-date semantics and lost priorities before explicit Apply.

Forecasts use Monday–Friday workdays and optional earliest bounds. No holidays,
partial days, resource leveling, portfolios, accounts or synchronization. Finish
deltas count calendar days. Limits: 100 tasks, durations 1–60 workdays, dates
2000–2100, common chart horizon 730 days. Baselines are snapshots, not approval.

Valid edits autosave locally. Storage denial is visible; corrupt or old application
JSON bytes remain protected until explicit Apply/reset and can be downloaded.
Browser storage is not durable backup or sync; file-origin support varies. There
is no runtime API, CDN, remote script or application build dependency.

## Three maintained development directions

Clone the history before running Git comparisons:

```sh
git clone example/gantt/history/gantt.bundle ../gantt-history
python -m specspec --root ../gantt-history diff \
  --base stage/01-code --target stage/02-spec --json
python -m specspec --root ../gantt-history diff \
  --base stage/02-code --target stage/03-spec --json
```

| Stage | Spec / code tags | Change |
| --- | --- | --- |
| 01 | `stage/01-spec` / `stage/01-code` | Portfolio, weekday forecasts, owners/rollups; cloud/leveling remain candidates |
| 02 | `stage/02-spec` / `stage/02-code` | Personal manual calendar dates/weekends/priorities; **13/17 live nodes withdrawn** |
| 03 | `stage/03-spec` / `stage/03-code` | Workshop durations/prerequisites/earliest bounds/baseline; **9/16 live nodes withdrawn** |

Each spec checkpoint precedes its runnable implementation. The first has no app
code; later specs retain the previous prototype. The final graph has **44 nodes:
22 live, 22 withdrawn**. Withdrawn reasoning retains identity, body, parents and
sources across each redirect. New workshop reasoning is separately justified.
No approval stages, confidence scores or installed hooks are involved.

- `history/cli.jsonl`: actual current CLI argv/stdin/results from reconstruction.
- `history/revisions.json`: real fixture commit IDs, receipt ordinals and withdrawal sets.
- `history/gantt.bundle`: complete standalone current-schema Git history.
- [History walkthrough](history/WALKTHROUGH.md): clone, diff and optional worktrees.

This is an intentional rewritten fixture, not a claim that the original older
commits used today's encoding. It preserves app evolution while removing obsolete
SpecSpec machinery. No nested `.git` is installed in this checkout and unrelated
SpecSpec commits are not rewritten. Persisted app JSON conversion remains tested;
it is distinct from unsupported obsolete SpecSpec node schemes.

## Explore the working graph

Install the development package from the parent checkout, then:

```sh
python -m specspec --root example/gantt validate --warnings-as-errors
python -m specspec --root example/gantt list --live --json
python -m specspec --root example/gantt list --retired --json
python -m specspec --root example/gantt context <full-id> --json
```

IDs are canonical padded Base64url over five random bytes (40 bits), including `=`.
The same equals sign separates the ID from the filename summary. Manual Markdown
edits are allowed and structurally validated; CLI/UI editing remains recommended.
Do not reinitialize the graph. Open this folder in VS Code for its independent view.

## Checks

```sh
npm --prefix example/gantt test
npm --prefix example/gantt run test:browser
python example/gantt/history/verify.py
python example/gantt/history/verify.py --history
```

Node 22+ is needed for the optional installed-Chromium browser harness. No npm
install or browser download is needed. `GANTT_BROWSER` selects Chrome/Chromium/Edge;
`GANTT_SCREENSHOT_DIR` saves optional screenshots. Tests use loopback and disposable
profiles. Previous real Windows browser evidence covers forecasts/baselines,
responsive native caret/drafts, cycles/deletion, literal text, downloads/upload,
preview/cancel/v1 conversion and protected/denied storage. That is not exhaustive
accessibility/browser-matrix/performance/security evidence or a remote CI claim.

Before an authorized parent-checkout commit, validate both exact staged graphs:

```sh
python -m specspec hook check
python -m specspec --root example/gantt hook check
```

Tests clone the maintained history temporarily; normal working files still belong
to the parent checkout's Git index. No local hook is installed automatically.

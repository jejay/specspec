# A planning app that changes its mind

A runnable **spec-aware** Gantt/planning example, developed with SpecSpec from its
first step. The [simulated user/AI conversation](STORY.md) includes **two major
redirects**, not just renamed nodes. The dialogue is fictional; the managed graph,
code, tests, and ordered Git commits are real.

## Try the final app

Open [`index.html`](index.html) in a modern browser. There is no build, account,
installation, runtime API, CDN, or remote script. For predictable browser-local
storage, use a stable local origin instead of `file://`:

```sh
# From the SpecSpec repository root:
python -m http.server 8000 --bind 127.0.0.1 --directory example/gantt
# Visit http://127.0.0.1:8000
```

1. Click **Capture baseline**.
2. Select **Prepare materials**, change its duration from 3 to 6 workdays, and save.
3. The workshop finish moves from April 20 to April 21. The baseline stays unchanged;
   current/baseline bars and the date table explain the changes.
4. Add/edit/remove tasks and finish-to-start prerequisites. Cycles and deleting a
   referenced prerequisite are rejected without detaching links or losing the draft.
5. Export JSON, or preview [`history/personal-v1.json`](history/personal-v1.json).
   Conversion warnings explain the changed weekend/end-date semantics and lost
   priorities. The preview does not replace work until explicit **Apply**.

Forecasts use Monday–Friday workdays and optional earliest bounds. Holidays,
partial days, resources, leveling, project portfolios, accounts, and synchronization
are **not implemented**. Finish deltas count **calendar days**. Practical limits:
100 tasks, duration 1–60 workdays, dates 2000–2100, combined chart horizon 730 days.
A baseline is a saved full-plan snapshot, not an approval state.

Valid changes autosave in this browser. Storage denial/failure is visible and the
app remains usable in memory. Corrupt or v1 saved bytes are never silently overwritten:
preview/apply conversion or explicitly reset; protected original bytes can be
downloaded. Export a file for backup. Browser storage is not durable backup or sync;
file-origin storage behavior varies by browser.

## Three real development directions

| Stage | Intentions before code | Runnable implementation | What changed |
| --- | --- | --- | --- |
| 01 | `3ba86c0` | `8ac5676` | Business portfolio, weekday forecasts, owners/rollups; cloud and leveling only unimplemented candidates |
| 02 | `f656942` | `f54142a` | Personal manual calendar ranges/weekends/priorities; **13 of 17 live nodes withdrawn** |
| 03 | `95be927` | `660af26` | Workshop durations/prerequisites/earliest bounds and explicit baseline; **9 of 16 live nodes withdrawn** |

Each spec-only checkpoint precedes its application rewrite and explicitly still
runs the previous prototype. Implementation commits add terminal evidence nodes.
Withdrawn bodies, IDs, parents, and source references are retained unchanged except
for withdrawal flags; their original code is in Git, not misleading current legacy
runtime branches. The final graph contains **44 nodes: 22 live, 22 withdrawn**.

The manifesto and common readable/safe/revisable intentions survive both pivots.
Local autosave, portability, and the browser-storage choice also survive pivot two.
The new workshop weekday algorithm is separately justified; it does **not** restore
or approve the old portfolio conclusion. No proposed/accepted stages, scores, review
quotas, nested Git repository, fabricated commits, or installed hooks are involved.

- [`STORY.md`](STORY.md): back-and-forth, rationale, scope limits, and actual checks.
- [`history/cli.jsonl`](history/cli.jsonl): actual CLI argv, input text, fingerprints,
  changed IDs, ancestor/impact reads, exit codes, and diagnostics—not generated hashes.
- [`history/revisions.json`](history/revisions.json): real predecessor/spec/code SHAs,
  graph fingerprints, and exact withdrawal sets. Code SHAs are filled in by the next
  commit so no file pretends to know the hash of its own containing commit.
- [`history/WALKTHROUGH.md`](history/WALKTHROUGH.md): inspect changes and recover old
  runnable prototypes without altering your current working tree.

## Explore the independent graph

Install SpecSpec in the active Python environment (`python -m pip install -e '.[dev]'`
from the parent checkout), then from the repository root:

```sh
python -m specspec --root example/gantt validate --warnings-as-errors
python -m specspec --root example/gantt list --live --json
python -m specspec --root example/gantt list --retired --json
python -m specspec --root example/gantt context fc2a2b2f-a7b0-4980-87d9-4f57101445a2 --json
python -m specspec --root example/gantt diff --base 8ac5676 --target f656942 --json
python -m specspec --root example/gantt diff --base f54142a --target 95be927 --json
```

From this folder an installed `specspec` discovers its nearest `_specspec/`, not the
parent graph. Open **this folder** in VS Code to explore it with SpecSpec. Canonical
Markdown editing through the CLI/UI is recommended; don't reinitialize this graph.
The working graph is now format 3 with no hashes. Manual edits are allowed if schema
and relationships remain valid. Archived API-2 receipts retain their original hash
strings and --expect arguments as historical evidence, not current requirements.

## Checks

Node 22+ is needed for the optional browser harness. No npm install is necessary:

```sh
npm --prefix example/gantt test                    # 20 model tests
npm --prefix example/gantt run test:browser        # installed Chromium, disposable profile
python example/gantt/history/verify.py             # graph + real CLI receipt chain
python example/gantt/history/verify.py --history   # also requires full original Git history
```

`GANTT_BROWSER` can select an installed Chrome/Chromium/Edge executable. No browser
is downloaded. The harness serves only app assets on loopback, uses a disposable
profile/debugger, then removes it. `GANTT_SCREENSHOT_DIR` optionally captures images.
The real Windows Chromium check passed forecast/baseline, native responsive caret,
cyclic drafts/deletion safety, literal project text, actual downloads/file upload,
preview/cancel/v1 conversion, reload, protected storage, session-only failure paths,
and direct local-file launch. Desktop/narrow screenshots were inspected.

The browser tests dispatch DOM actions and validate real layout/files/storage;
they are not exhaustive manual, accessibility, browser-matrix, performance, or
production-security certification. Remote CI is configured but not claimed run.

Before an authorized commit, stage the complete intended change and validate both
**exact index snapshots** from the repository root:

```sh
python -m specspec hook check
python -m specspec --root example/gantt hook check
```

No local hook is installed; the two graphs share ordinary parent-repository Git.

# Contributing to specspec

specspec specifies itself. The graph in `.specspec/` is the design record for this
repository: before changing behavior, read the relevant nodes with their ancestors
(`python -m specspec query ID --max-distance 0 --with-ancestors`), and keep
implementation nodes and their `sources` current with the code. Coding agents follow
[AGENTS.md](AGENTS.md); the [README](README.md) explains the concepts.

## Repository layout

| Path | Contents |
| --- | --- |
| `src/specspec/`, `pyproject.toml` | Python library and CLI, the domain authority for every host |
| `graph-ui-common/` | Shared renderer and host session used by both editors |
| `vscode/` | VS Code adapter; its README is the editor guide shipped in the VSIX |
| `electron/` | Sandboxed desktop adapter and portable packaging |
| `package.json`, `package-lock.json` | One private npm workspace with root scripts and the only lockfile |
| `.specspec/` | This product's own specification graph |
| `example/gantt/` | Runnable example and tracked snapshot of its independent Git history |
| `branding/`, `docs/images/` | Imported brand assets and README figures |
| `tools/` | Release, icon, figure and palette tools, and the agent-guide quiz |

## Development setup

Use Python 3.11+, Git, Node 22.12+ and npm 10+:

```sh
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1 or source .venv/Scripts/activate
python -m pip install -e '.[dev]'
npm ci
```

Run the development CLI as `python -m specspec`. The editors default to the
`specspec` on PATH; point them at the development build instead:

```sh
npm run desktop -- --python .venv/Scripts/python.exe --project .   # Linux: .venv/bin/python
```

In VS Code, F5 from the repository root starts **Run specspec on this repository** in
a separate development window. The generated `.vscode/settings.json` stays local.

| Command | Result |
| --- | --- |
| `npm run build` | Compile both UI adapters |
| `npm test` | Shared UI, VS Code adapter and Electron unit suites |
| `npm run test:host:vscode` | Real VS Code in an isolated profile (set `SPECSPEC_PYTHON`) |
| `npm run test:host:electron` | Real Electron in an isolated profile (set `SPECSPEC_PYTHON`) |
| `npm run package:cli` | Python wheel and source distribution in `dist/` |
| `npm run package:vscode` | Versioned VSIX in `dist/` |
| `npm run package:electron` | Current-platform portable folder and archive in `dist/` |
| `npm run package:all` | All artifacts, with content and version inspection |
| `npm run verify:packages` | Recheck artifacts and write a manifest and SHA256SUMS |

## Checks

These match CI and AGENTS.md:

```sh
python -m specspec check --sources --warnings-as-errors
python -m specspec --root example/gantt check --sources --warnings-as-errors
python -m ruff check .
python -m ruff format --check .
python -m pytest
npm test
python example/gantt/history/verify.py --history
```

Source anchors refer to Git objects, so `check --sources` needs the full history
(CI checks out with `fetch-depth: 0`). Before a commit, stage the complete intended
change and run both graph checks with `--staged`; they validate the exact index.

## Releasing

All products share one version: `pyproject.toml`, `specspec.__version__`, the four
npm `package.json` files and their lockfile entries change together, and so do the
default of `pipy_publish.yaml` and the `VERSION` of `tests/test_release.py`.

1. When the agent guide changed since the newest release on PyPI, copy that release's
   guide to `src/specspec/templates/earlier/<version>.md`, so that `specspec guide` can
   replace it. The publish workflow checks this.
2. Give the version a section `## X.Y.Z` in CHANGELOG.md; it becomes the GitHub
   release notes.
3. Build and inspect locally with `npm run package:all` and `npm run verify:packages`.
   Local builds never publish.
4. Commit and push the release revision to `main`.
5. Run **Actions → Publish CLI to PyPI** with the exact version. The `build` job tests,
   builds and smoke-tests the wheel and source distribution; only the separate
   `publish` job receives the short-lived OIDC identity for PyPI's trusted publisher
   (repository `jejay/specspec`, workflow `pipy_publish.yaml`, environment `pypi`).
6. Push the tag `vX.Y.Z` on that revision. **Build release artifacts** checks that the
   tag names the version and is on `main`, builds the editors on Windows and Linux and
   creates the GitHub release with the VSIX, both desktop archives and `SHA256SUMS`.
7. Confirm the files on [PyPI](https://pypi.org/project/specspec/) and the GitHub
   release, and test a fresh `uv tool install specspec`.

Signing, Marketplace submission and hook changes each need their own explicit
authorization, and so does every tag.

## Maintaining the Gantt example history

`example/gantt/` is a tracked snapshot; its real history is the bundle in
`example/gantt/history/gantt.bundle`. `python example/gantt/history/checkout.py
[DESTINATION]` clones it outside this repository for manual use, and
`python example/gantt/history/verify.py --history` checks every revision.

Every node-format change rebuilds that entire history with current tools, as if it
had always used today's specspec; [the walkthrough](example/gantt/history/WALKTHROUGH.md)
gives the procedure. The example's README, AGENTS.md and STORY.md are part of that
history, so edit them through a bundle update.

## Branding, figures and tools

`branding/` holds byte-identical imports from the final brand kit, with sources and
digests in `branding/identity.sha256.json`; `python tools/build_icon.py` regenerates
the Windows launcher icon. `python tools/readme_figures.py` redraws the README
figures in `docs/images/` (it needs `fonttools` and the brand kit's Manrope font). The
palette playground is `tools/rainbow-playground/index.html`; open it directly in a
browser to explore and export node palettes.

## Quizzing models on the agent guide

`tools/guide_quiz/` checks a wording of the agent guide against models. A model gets one
guide version as its only instruction and solves quizzes: dilemmas with one keyed answer
and open tasks, such as drawing a graph from an owner's brief, revising one, reviewing
nodes the owner edited by hand or writing the commands for a change. A stronger model
grades the open answers without knowing which model or guide produced them. specspec's
own validator checks every drawn graph, and its command line runs the commands of an
answer on a temporary copy of the task's graph.

```sh
python -m tools.guide_quiz guides                    # guide versions and their sizes
python -m tools.guide_quiz dilemmas --guides shipped,2026-11-10-before-structure-rules
python -m tools.guide_quiz tasks --tasks clinic,bakery,toolshed,discuss-game
python -m tools.guide_quiz grade                     # the grader's verdicts and the command runs
python -m tools.guide_quiz scorecard --guides 2026-11-10-before-structure-rules,shipped
python -m tools.guide_quiz report --guides shipped,2026-11-10-before-structure-rules
python -m tools.guide_quiz agreement --graders claude-opus-5-5,claude-haiku-5-5
python -m tools.guide_quiz costs
```

Every guide name is a file in `tools/guide_quiz/guides/`. `shipped` stands for the package
template and resolves to the dated file with the same content, so that every result names
a text that stays; after changing the shipped guide, copy it there under a new dated name
before you quiz it. The default model is Claude Haiku 5.5, the weakest model the guide is
written for; `--models` takes others. A wording to try out is a file under
`guides/experiments/`: a trimmed guide is quizzed like any other version, and the cuts
that leave the results where they were are candidates for the shipped guide.

`scorecard` is the place to start reading results: about thirty behaviours, each with a
sentence on what the model was asked and what is counted, one column per guide in the
order given. Its first group holds what counts most, whether the agent tells intention
from conclusion: "an intention you left unsaid is worded above your way", "a statement
that works against the manifesto is raised". The other groups follow, such as "your edits
left as you wrote them". `report` prints every criterion behind those rows.

Calls go through the `claude` command of Claude Code under your own login and cost money,
so no test and no CI job makes them; `costs` adds up what the recorded calls cost. Grading
by Claude Opus 5.5 is most of that: `grade --guides` limits it to the guide versions you
compare, and `agreement` shows, criterion by criterion, where a cheaper grader comes to
the same verdicts. Runs are resumable: answers already given are kept under the name of
their task or dilemma. An answer carries a mark of the brief it was given and stops
counting when the brief's wording changes; a dilemma whose wording changes gets a new ID.
After a change to a rubric, `grade --again TASK` judges that task's answers anew. Raw
answers stay in the ignored `tools/guide_quiz/results/`; put the numbers that justify a
wording into the commit message.

# A planning app that changes its mind

A worked **spec-aware** example, with an independent graph in `_specspec/`.
The [simulated dialogue](STORY.md) records the initial business-portfolio direction.
Later commits will record two substantial redirects and runnable implementations.
Nothing in the dialogue is a real client's instruction or technical sign-off.

The graph is initialized **before any application code**. Original intentions and
AI conclusions are separate nodes. CLI receipts are in `history/cli.jsonl`;
`history/revisions.json` connects the narrative to real Git commits. This folder
uses the parent repository's Git history; it is not a nested repository.

From the SpecSpec repository root, after installing `.[dev]`:

```sh
python -m specspec --root example/gantt list --json
python -m specspec --root example/gantt validate --warnings-as-errors
python -m specspec --root example/gantt list --retired --json
```

From this folder the installed `specspec` discovers the nearest graph. Open this
folder in VS Code to browse this project's graph, rather than the parent graph.
Do not run `init` again or edit canonical frontmatter by hand.

## Current stage 02: manual personal planning

Open `index.html` in a modern browser, or run from this folder:

```sh
python -m http.server 8000 --bind 127.0.0.1
# Visit http://127.0.0.1:8000
node --test test/*.test.cjs
```

The editable local personal app uses manually entered inclusive start/end dates,
weekends, and priorities. Valid edits autosave locally; failures are surfaced and
corrupt stored bytes stay protected until reset. Import/export uses version-one JSON.
Seven model tests and JS syntax checks passed; real-browser checks are not yet claimed.

Redirect one withdrew 13 of 17 live nodes and replaced the portfolio/team/service/
scheduler branch. Its original code remains in Git (`gantt: 01 implement ...`), not
in a misleading current "legacy" runtime. `history/personal-v1.json` is a real demo
export. No approval metadata or nested Git repository was introduced.

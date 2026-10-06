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

## Stage 01: first hypothesis

Open `index.html` in a modern browser, or run from this folder:

```sh
python -m http.server 8000 --bind 127.0.0.1
# Visit http://127.0.0.1:8000
node --test test/*.test.cjs
```

The read-only local portfolio/calendar prototype implements weekday dependency
forecasts, named-owner display, task progress, and project finish/progress rollups.
Six model tests and JS syntax checks passed. Real-browser checks are not yet claimed.
Shared accounts, hosted storage, and resource leveling remain **unimplemented**.

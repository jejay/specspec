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
| `tools/` | Release, icon, figure and palette tools |

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
npm `package.json` files and their lockfile entries change together.

1. Build and inspect locally with `npm run package:all` and `npm run verify:packages`.
   Local builds never publish.
2. Commit and push the release revision to `main`.
3. Run **Actions → Publish CLI to PyPI** with the exact version. The `build` job tests,
   builds and smoke-tests the wheel and source distribution; only the separate
   `publish` job receives the short-lived OIDC identity for PyPI's trusted publisher
   (repository `jejay/specspec`, workflow `pipy_publish.yaml`, environment `pypi`).
4. Confirm the files on [PyPI](https://pypi.org/project/specspec/) and test a fresh
   `uv tool install specspec`.

Tags, signing, Marketplace submission and hook changes each need their own explicit
authorization.

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

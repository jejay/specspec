# Work on the specspec monorepo

Start with the [product introduction](README.md), [architecture](docs/architecture.md)
and [current specification tour](docs/own-spec.md). The binding graph is `.specspec/`;
repository-specific agent instructions are in [AGENTS.md](AGENTS.md).

## One checkout, separate products

- Python owns canonical schema, graph rules, Markdown plans, transactions and Git.
- `graph-ui-common` owns the shared renderer and guarded host/session behavior.
- `vscode` and `electron` own their native lifecycle, trust and persistence adapters.
- One private root npm workspace/lock supplies JavaScript build/test dependencies.
  Do not run independent installs or add nested lockfiles. Existing
  `npm --prefix FOLDER run SCRIPT` invocations still run scripts, not separate installs.

## Development setup

Use Python 3.11+, Git, Node 22.12+ and npm 10+:

```sh
python -m venv .venv
# Activate one of:
# Bash on Linux/macOS: source .venv/bin/activate
# Git Bash on Windows: source .venv/Scripts/activate
# PowerShell on Windows: .venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
npm ci
```

Developer-only dependencies include test/format/build tools and Pillow for
regenerating the tracked Windows icon. CLI end users need only the runtime package.
If activation is unavailable, invoke `.venv/Scripts/python.exe` on Windows or
`.venv/bin/python` explicitly and put its directory on PATH for npm's Python scripts.
No global npm installation or Marketplace credentials are required.

For normal product use, install the CLI with `uv tool install .` or `pipx install .`
instead. An editable development environment and a global installation can coexist;
select the intended executable explicitly when testing changes.

## Root commands

| Command | Result |
| --- | --- |
| `npm ci` | Install all three workspaces from the single lock |
| `npm run build` | Compile/bundle both UI adapters |
| `npm run build:vscode` | Compile the extension and copy shared assets/runtime |
| `npm run build:electron` | Build the desktop's shared assets/runtime |
| `npm run desktop -- --project .` | Build and open this checkout in Electron |
| `npm test` | Shared UI, VS Code adapter and Electron unit suites |
| `npm run test:host:vscode` | Real installed VS Code in an isolated test profile |
| `npm run test:host:electron` | Real Electron in an isolated test profile |
| `npm run package:vscode` | Local versioned VSIX in `dist/`; does not install it |
| `npm run package:cli` | Python wheel/source distribution in `dist/` |
| `npm run package:electron` | Current-platform portable folder and archive |
| `npm run package:all` | Build all artifacts and inspect their contents/versions |
| `npm run verify:packages` | Recheck artifacts and write a manifest/SHA256SUMS |

The Python packaging/archive commands use the active `python` executable. Runtime
UIs default to the globally installed `specspec`. For an editable development CLI:

```sh
# Git Bash/PowerShell on Windows; paths relative to repository root:
npm run desktop -- --python .venv/Scripts/python.exe --project .
# Linux:
npm run desktop -- --python .venv/bin/python --project .
```

VS Code F5 from this root runs **Run specspec on this repository** in a separate
development window/profile using its tracked launch/task/workspace files. Opening
`vscode/` and **Run specspec Extension** is an alternative. Both require root
`npm ci` and the development Python environment. For actual user installation,
build/install the [VSIX](vscode/README.md) instead; a development host is optional.
The generated root `.vscode/settings.json` remains machine-local and ignored.

## Checks

With the development environment active:

```sh
specspec check --warnings-as-errors
specspec check --sources --warnings-as-errors
python -m ruff check .
python -m ruff format --check .
python -m pytest
npm test
python example/gantt/history/verify.py --history
```

Real-host tests require an installed VS Code and a working Electron sandbox. Set
`SPECSPEC_PYTHON` to the absolute development interpreter; `VSCODE_EXECUTABLE`
overrides discovery. They clone the maintained example externally and use disposable
profiles, never the owner's installed extension profile. Diagnostic artifacts stay
available on failure. Physical/platform scope and aggregate budgets are documented
in [host evidence](docs/investigations/host-smoke.md).

## Specification and examples

Read relevant bindings and every ancestor before changing behavior:

```sh
specspec query NODE_ID --max-distance 0 --with-ancestors
specspec diff --with-context
```

Preserve owner changes and Git authorization. Keep meaningful choices separate from
their intentions, keep source explanations current, and validate the complete graph.
Before an authorized commit, stage the intended coherent graph/code slice and run
`specspec check --staged --sources --warnings-as-errors` on that exact index; also
check `specspec --root example/gantt check --staged --sources --warnings-as-errors`
when maintained fixtures change. Builds/tests do not stage, commit or install hooks.

The tracked Gantt directory is not a Git workspace. Use
`python example/gantt/history/checkout.py` for a new external clone. Every canonical
scheme change requires rewriting its **entire maintained history** through actual
current tools; follow the [maintenance procedure](example/gantt/history/WALKTHROUGH.md).
Preserve IDs, application behavior, manual experiments and unrelated product history.

## Branding and releases

Builds use selected assets in `branding/`, not a sibling checkout. Imports retain
source digests and exact bytes; keep UI status colors independent. Regenerate the
Windows launcher with `python tools/build_icon.py` only when its source changes.

[The local release procedure](docs/releasing.md) covers artifact inspection,
fresh-environment installs and platform qualification. Publication, tags, signing,
owner hook changes and Marketplace submission require separate explicit authorization.

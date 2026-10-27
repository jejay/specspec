# specspec Desktop

A standalone Windows/Linux graph editor using the **same renderer and guarded
session as the VS Code extension**. Connect intentions, separately revisable choices
and actual implementation in local, Git-versioned Markdown.

This is the early **0.1** desktop: portable, unsigned, without installers,
auto-updates or a bundled Python runtime. CLI and Git remain external prerequisites.
There is no hosted service or built-in coding-agent connector.

## Run from the monorepo

Install the CLI globally first: from the repository root, `uv tool install .` or
`pipx install .`. Check `specspec --version` in the shell used to launch the app.
Then use Node 22.12+ and npm 10+:

```sh
# All commands from the repository root:
npm ci
npm run desktop
# Alternative: authorize this checkout as the initial project:
npm run desktop -- --project .
```

The default launcher invokes `specspec` on PATH, not a project-specific Python.
Choose **Open project**, select a containing folder and explicitly **Trust and Open**.
An explicit `--project` authorizes that launch folder instead. Never pass project or
executable paths from untrusted content. Discovery selects the nearest `.specspec/`
entry, including an invalid one; it does not silently fall back to a parent.

Root scripts interpret relative launch paths from the repository root. To test an
editable development environment, use one of:

```sh
# Windows, from the root:
npm run desktop -- --python .venv/Scripts/python.exe --project .
# Linux, from the root:
npm run desktop -- --python .venv/bin/python --project .
```

The workspace-local `npm --prefix electron start` still runs from `electron/`;
its equivalent relative Python/project arguments are `../.venv/...` and `..`.
Root scripts avoid that cwd surprise.

## Portable package

Activate the [developer Python environment](../CONTRIBUTING.md) for the standard-
library archive helper, then run from the repository root:

```sh
npm ci
npm run package:electron
```

Output follows the current Node platform/architecture:

- `dist/desktop/specspec-desktop-win32-x64/` and `dist/specspec-desktop-0.1.0-win32-x64.zip`, or
- `dist/desktop/specspec-desktop-linux-x64/` and `dist/specspec-desktop-0.1.0-linux-x64.tar.gz`
  (other supported Node architectures use their own suffix).

Extract the whole archive and run `specspec-desktop.exe` or `./specspec-desktop`. Keep resources,
Chromium/Electron licenses and shared-library notices together. End users need
**the global CLI and Git, not Node/npm**. Linux archives retain executable modes;
keep the Chromium sandbox enabled and satisfy its OS prerequisites. macOS packaging
is not supplied; the CLI/VS Code are alternatives there. Cross-building or CI
configuration alone is not proof of execution on a target OS.

The package contains only the selected application entry points, compiled shared
runtime/assets and licenses, with the selected launcher icon. It does not carry
source test harnesses, sibling branding workspaces, npm dependencies or a Python
installation. [Release inspection/checks](../docs/releasing.md)

## Executable and project settings

If PATH does not reach the CLI, set trusted launch environment `SPECSPEC_COMMAND`
to its absolute executable and `SPECSPEC_ARGS` to `[]`. `SPECSPEC_PYTHON` or `--python`
selects a specific interpreter with `-m specspec`. `SPECSPEC_ARGS` is a JSON string
array, not a shell command. These settings are not read from project files or
exposed to the renderer.

Path-bearing executable settings are resolved once from the launch directory,
before project subprocess cwd changes. Bare names such as `specspec` and `python`
use PATH. Project switching does not rebase an explicit executable path.

To explore Git comparisons, create the independent Gantt workspace with
`python example/gantt/history/checkout.py` and select that clone. The tracked
`example/gantt/` snapshot is not a standalone Git repository.

## Opening and initializing projects

The app checks the configured specspec CLI immediately, even before project selection.
If it is unavailable, a blocking installation screen offers Retry; the app never
installs it automatically. **Open project** and **Ctrl/Command+O** choose a trusted
local directory. There is no application menu bar. An empty project offers a centered
manifesto form and **Initialize specspec** action, which initializes Git when needed
and creates or appends AGENTS.md through the CLI. Broken existing graphs remain
repair cases, never initialization targets.

## Editing, local state and safety

The shared UI supplies native forms, graph navigation, color modes, source previews,
spotlights, selected deletion and current-schema revision comparisons. **Ctrl+S**
saves the focused managed form. Compare revisions uses bounded native input;
historical views are read-only. Workspace views compare against fresh HEAD, with
D ghosts retained through staging and disappearing after commit.

Manual Markdown edits are allowed. Watchers reconcile external files while retaining
drafts/caret/camera; invalid graphs display their current broken relationships and
diagnostics with safe forms still editable. Unreadable targets retain repair access;
unavailable loads retain marked last-usable context rather than enabling stale writes.
Same-node external changes and destructive actions receive native confirmation.

Polling is off by default. `--poll-interval-ms 5000` or trusted launch environment
`SPECSPEC_POLL_INTERVAL_MS=5000` enables a supplement; `0` disables it. Watchers are
filesystem-dependent hints and explicit Refresh remains available.

Presentation and dirty drafts live by project in `graph-presentation.json` under
Electron's normal user-data directory. The renamed app defaults to the
`specspec-desktop` profile name. Existing older profile directories are preserved;
finish/save drafts before upgrading, or explicitly launch with `--profile PATH`
to continue using that trusted existing profile. Corrupt bytes are protected and storage is
bounded, with no silent eviction. A new portable executable does not migrate or
remove that state. Preserve drafts and project `.specspec/local/` recovery data;
`specspec recover` handles interrupted managed transactions, not arbitrary Undo.
Process recovery is not guaranteed power-loss durability or backup.

The sandboxed/context-isolated renderer has no Node/FS/spawn API. Main owns trusted
CLI execution and project authorization. Requests/navigation/popups/permissions
remain restricted to the local application boundary; setup downloads are distinct
from runtime renderer requests. These protections are bounded, not a security
certification. Source symbols are descriptive; graph validity is not semantic proof.

## Checks

From the monorepo root:

```sh
npm test
npm run test:host:electron
```

The host runner uses a disposable profile and an external clone of maintained Gantt
history. `SPECSPEC_PYTHON` selects the test CLI interpreter;
`SPECSPEC_DESKTOP_EXECUTABLE` selects an unpacked portable executable for artifact
qualification. It checks actual saves, native consent, watchers/invalid drafts,
source/spotlight behavior, reload persistence, historical switching and sandbox
boundaries. It never installs owner hooks or changes a real product.

[Platform scope](../docs/platforms.md) and [release evidence](../docs/investigations/release-0.1.md)
distinguish executed Windows checks from unexecuted targets. Physical Linux/macOS,
every filesystem, all accessibility/performance poses and remote transports are
separate qualification. Production behavior and individual test deadlines remain
independent of the harness's aggregate budgets.

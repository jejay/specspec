# SpecSpec Desktop — initial Electron adapter

A local Linux/Windows window using **exactly the same graph UI/session as VS Code**.
This is a runnable initial slice, not a signed installer, bundled Python distribution,
auto-updater, production security certification, or Claude Code/Codex connector.

## Run from this checkout

Use Node **22.12+**, npm, Git and a Python environment with the local SpecSpec CLI.
From the repository root:

```sh
python -m pip install -e '.[dev]'  # In your development Python environment.
npm --prefix graph-ui-common ci
npm --prefix electron ci
npm --prefix electron start
```

The first runtime launch downloads the pinned Electron framework if absent; this is
installation, not a renderer/CDN dependency. The app itself makes no remote requests.
Click **Open project**, choose a folder and explicitly **Trust and Open**. Discovery
finds the nearest `_specspec/`, including `example/gantt`. A configured, trusted CLI
executable is run in the main process; project content cannot choose it.

For an explicit interpreter and authorized initial folder (paths are interpreted
from the Electron process's **launch directory**, normally `electron/` under npm).
Explicit interpreter/CLI paths are made absolute at launch, before the subprocess
cwd switches to a selected project; choosing another graph does not rebase them.
Bare executable names such as `python`, `specspec`, and `uvx` continue to use PATH:

```sh
# Linux, with the repository's .venv:
npm --prefix electron start -- --python ../.venv/bin/python --project ..
# Windows (PowerShell or Git Bash):
npm --prefix electron start -- --python ../.venv/Scripts/python.exe --project ..
# The worked example:
npm --prefix electron start -- --python ../.venv/Scripts/python.exe --project ../example/gantt
```

`SPECSPEC_PYTHON` supplies an interpreter with `-m specspec`. Alternatively use
`SPECSPEC_COMMAND` and `SPECSPEC_ARGS` (a JSON string array, e.g. `uvx` / `["specspec"]`)
for an installed isolated CLI. These trusted launch settings are not read from project
files or exposed to the renderer. An explicit `--project` is authorization by the
local launcher; don't pass untrusted folder/executable paths. An invalid nearest
canonical directory is diagnosed rather than silently falling back to its parent.

Graph controls, native inline editing, cameras, min/max colors, hover, withdrawal,
migration and revision overlays are shared. **Compare revisions** uses a native HTML
modal with bounded base/target input; an empty target means workspace. Historical
views are read-only. Native confirmations protect retire/restore/migrate and
saving a draft over externally changed node contents.

Markdown edits outside the tool are allowed. File watchers reload the graph by
default, including canonical-directory replacement/recreation. Optional polling is
disabled: enable with `--poll-interval-ms 5000` or `SPECSPEC_POLL_INTERVAL_MS=5000`;
`0` turns it off. This trusted launch setting is not taken from project content.
Events are coalesced and incomplete saves get bounded retries; unchanged data does
not redraw. Invalid files retain the last graph marked out of date and disable
mutations until valid. Watcher errors are visible; no hidden polling is enabled.
Explicit Refresh remains available, particularly for filesystems that miss events.

Presentation preferences and dirty drafts are scoped by project in
`graph-presentation.json` under Electron's normal user-data directory. They retain
original node contents, including after reload, and do not modify canonical metadata.
Corrupt saved bytes remain protected with a visible error; move that file aside
explicitly to reset. Storage has limits and never silently evicts retained drafts.
This is not guaranteed power-loss durability or backup; export/manage the actual
specification in Git as usual. A failed renderer can be recovered by restarting the
app; no writer/recovery artifacts are silently cleaned.

## Packages and checks

```sh
npm --prefix electron test
npm --prefix electron run test:host
npm --prefix electron run package
```

Packaging produces an unpacked portable app under `electron/release/` for the current
platform. For an explicit target use `npm --prefix electron run package -- --platform=linux`
or `--platform=win32` (cross-building is not proof that it runs on that OS). Python/Git
remain external prerequisites. Packaging and dependency licenses are retained; signing,
installers and publication are separate work. `npm audit` reports no known findings
for the pinned dependency trees at the time of this implementation, not a security guarantee.

The real Windows host test uses a disposable CLI-managed/Git graph and profile,
loopback-only Chromium debugging, and the same real canvas regression harness as
VS Code. It checks A/M/D and live theme tokens, sandbox/no Node/blocked requests and
popups, actual saving, manual-file watcher sync, invalid-file/draft preservation, reload persistence and actual
historical/workspace switching. `SPECSPEC_SCREENSHOT_DIR` captures diagnostics;
`SPECSPEC_PYTHON` selects the test interpreter. No real project is mutated or hook
installed by these tests. DOM-dispatched tests/screenshots are not exhaustive manual,
accessibility, performance, cross-device or adversarial-filesystem evidence.

Linux is targeted by platform-neutral code and a CI/Xvfb smoke job. It has **not been
run locally on Linux**; remote CI is not claimed completed. Keep Electron's sandbox
on; Linux environments may need a working Chromium sandbox helper or user namespaces.
Claude Code/Codex integration remains a separately recorded future intention using
the common adapter seam, with transport, lifecycle and authorization still to decide.

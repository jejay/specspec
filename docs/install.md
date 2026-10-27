# Install specspec 0.0.1

Choose the CLI, the VS Code extension, the desktop, or all three. The CLI's default
installation source is [PyPI](https://pypi.org/project/specspec/). The visual products
share this monorepo but install independently; their source builds remain local.

## Prerequisites

| Product | Runtime | Building from source |
| --- | --- | --- |
| CLI (`specspec`) | Python 3.11+ and Git, including initialization | uv or pipx |
| VS Code (`specspec-vscode`) | VS Code 1.90+, global CLI and Git on the workspace host | Node 22.12+, npm 10+ |
| Desktop (`specspec-desktop`) | Windows/Linux, global CLI and Git | Node 22.12+, npm 10+; developer Python for release archives |

The CLI needs no Node, editor or source checkout. Portable desktop archives include
Electron, not Python or Git; the extension includes its JavaScript/assets, not the
CLI. Application renderers use bundled local assets.

## Install the CLI from PyPI

Use [uv tools](https://docs.astral.sh/uv/guides/tools/) or
[pipx](https://pipx.pypa.io/stable/installation/) for a user-wide command with isolated
Python dependencies:

```sh
uv tool install specspec
# Alternative, choose one installer:
# pipx install specspec
specspec --version
specspec --help
```

For an explicitly pinned installation use `uv tool install 'specspec==0.0.1'` or
`pipx install 'specspec==0.0.1'`. The unpinned command normally selects the latest
release. Do not add the CLI to every product's runtime, use administrator privileges,
or use `sudo pip`. Installation downloads packages; the CLI does not install itself
when a graph is opened. `uvx --from specspec specspec ...` is an optional one-shot
alternative; persistent installation is the normal human and visual-host setup.

### Make the command visible to your editor

If `specspec` is not found, run `uv tool update-shell` or `pipx ensurepath`, then open
a new terminal. Fully quit and reopen VS Code/Electron if they inherited an older
PATH. On Windows, `where.exe specspec` lists matching executables; on Linux/macOS use
`command -v specspec`. Check `specspec --version` in that same shell.

If an editor still cannot find it, configure an absolute executable path:

```json
{
  "specspec.command": "C:\\Users\\you\\.local\\bin\\specspec.exe",
  "specspec.args": []
}
```

Use your actual tool-bin path (`uv tool dir --bin` reports uv's). Configure the
machine hosting the workspace, not untrusted project text. An absolute interpreter
with specspec installed and arguments `["-m", "specspec"]` is a developer alternative.

Electron also defaults to `specspec` on PATH. Trusted launch environment
`SPECSPEC_COMMAND` and `SPECSPEC_ARGS=[]` can select its absolute executable.
`--python` / `SPECSPEC_PYTHON` are developer alternatives, not a requirement to create
a per-project environment. See [desktop launch details](../electron/README.md).

### Source and wheel alternatives

For development or qualifying an exact artifact, explicitly install a local checkout,
Git revision or wheel instead of the PyPI default:

```sh
uv tool install /path/to/specspec-checkout
uv tool install 'git+https://github.com/jejay/specspec.git'
uv tool install /path/to/specspec/dist/specspec-0.0.1-py3-none-any.whl
```

These are alternatives, not consecutive steps. pipx accepts the same inputs. A Git
URL without a ref follows the default branch, not an immutable release; use an
existing commit/tag when reproducibility matters. These instructions do not create
or assume a release tag. Building a CLI wheel uses `python -m build`; source UI
builds require the monorepo, not the Python-only source distribution.

## Install the VS Code extension locally

Only a UI source build needs a checkout. From its root:

```sh
git clone https://github.com/jejay/specspec.git
cd specspec
npm ci
npm run package:vscode
code --install-extension dist/specspec-vscode-0.0.1.vsix
```

If `code` is unavailable, use Extensions → … → Install from VSIX…, select that file
and reload. Open your product folder, trust it if appropriate, then run
**specspec: Open Graph**. Direct `.specspec/` node files use the graph custom editor;
Reopen Editor With → Text Editor keeps raw Markdown available.

No Marketplace account, personal access token or F5 development host is needed. The
local publisher identifier `specspec-dev` is an extension identity, not a Marketplace
listing. Packages contain compiled shared code/assets/notices; no runtime npm install
is needed on the target editor. [Extension guide](../vscode/README.md)

For SSH/tunnels, install the VSIX and PyPI CLI on the workspace host beside Git and
its real files. See [remote workspaces](remote-workspaces.md); browser-only virtual
filesystems are not supported. Remote execution has its own qualification scope.

## Run or package the desktop

From a monorepo checkout's root:

```sh
npm ci
npm run desktop
# Alternative: authorize this checkout directly:
# npm run desktop -- --project .
```

The first launch asks you to select and trust a project. Relative launch paths in
root scripts are relative to the repository root. Never supply untrusted executable
or project arguments. [Desktop guide](../electron/README.md)

For a portable build, activate the [developer Python environment](../CONTRIBUTING.md)
and run `npm run package:electron`. The unpacked app is under
`dist/desktop/specspec-desktop-PLATFORM-ARCH/`; the archive is
`dist/specspec-desktop-0.0.1-win32-x64.zip` or the corresponding Linux `.tar.gz`.
Architecture follows Node. Extract the whole archive, keep resources/licenses together
and run `specspec-desktop.exe` or `./specspec-desktop`. End users need the PyPI CLI
and Git, not Node/npm. Linux tar archives preserve executable permissions; keep
Chromium's sandbox enabled and satisfy OS prerequisites. Builds are unsigned,
without installers or auto-updates. Cross-building is not platform qualification.

## Create and open a project

```sh
mkdir my-project
cd my-project
specspec init -m "Test"
specspec query --max-distance 2
```

`init` requires Git, an existing directory and a nonempty manifesto. It initializes
Git when needed, creates `.specspec/<id>.md`, and creates root `AGENTS.md` or appends
the [shipped guide](agents.md) after its exact existing bytes. Unsafe instruction
targets are rejected. It protects `.specspec/local/` with a checkout-local Git
exclusion; it does not stage, commit, configure identity or install hooks. Replace
the smoke-test text above with a meaningful product goal.

Both UIs immediately check CLI compatibility. A missing CLI shows installation and
Retry; an authorized directory without a graph shows a centered manifesto form and
Initialize specspec action. Opening a folder alone never creates a graph. Broken
specifications remain repair cases. Electron has no menu bar; use its visible
project picker or Ctrl/Command+O. Existing graphs remain inspectable if Git is later
removed, with comparison limits reported. Full IDs include their final `=`.

## Upgrade and uninstall

For a normal unpinned PyPI installation:

```sh
uv tool upgrade specspec
# Or: pipx upgrade specspec
```

Update matching UI packages too: rebuild/reinstall the VSIX, using `--force` when
needed, or extract the new desktop archive into a new directory. Do not mix portable
resources from different versions. Preserve project files and local draft/recovery
state; consult the changelog before replacing an early-version tool.

**Replacing a pre-publication local build:** earlier development packages used
`0.1.0`; that is numerically higher than the first public `0.0.1`, so a normal
upgrade may not switch sources/downgrade. Explicitly replace it with
`uv tool install --reinstall --force specspec` or `pipx install --force specspec`,
then check `specspec --version` and restart the editor. This selects the public
PyPI source instead of silently continuing a saved checkout/wheel installation.

`uv tool uninstall specspec` or `pipx uninstall specspec` removes the CLI, not your
projects. Remove the extension through Extensions; deleting a portable app removes
its executable files, not specifications, Electron drafts or recovery data.

## Upgrading pre-release workspaces

The current directory is `.specspec/`, replacing development-only `_specspec/`.
Finish/recover interrupted writes with their matching old CLI and save buffers
before changing tools. Preserve experiments/backups, then explicitly rename without
overwriting an existing destination:

```sh
mv -- _specspec .specspec
```

PowerShell: `Rename-Item -LiteralPath _specspec -NewName .specspec`. Update your own
path references/editor setup, install matching tools, and run `specspec check --sources`.
Runtime data belongs in `.specspec/local/`: preserve the old runtime directory and
move it explicitly without overwriting an existing destination. Keep journals,
spotlights and diagnostics; no automatic legacy-state fallback is provided.

There is one current location, not a compatibility reader or migration command.
Working-tree renaming does not rewrite arbitrary history; old comparisons may be
absent/unavailable. Maintained Gantt histories are managed independently, and existing
manual clones are never reset. Internal schema/protocol fields remain machine details.

## Troubleshooting

- **Package unavailable:** check [PyPI](https://pypi.org/project/specspec/) and the
  [publishing workflow](releasing.md). A pending publisher alone is not an upload.
- **CLI failed to launch:** check host PATH/version and the absolute executable
  setting. In VS Code use View → Output → specspec.
- **Graph invalid:** use `query --issues --with-ancestors`, `query ID --raw` and
  `diff --with-context`. See [repair](invalid-graphs.md); invalidity does not authorize
  deleting descendants or changing relationships automatically.
- **Interrupted edit/init:** retain `.specspec/local/` and run `specspec recover`.
  Clear a stale lock only after confirming no writer is running. Exclusive-link
  publication requires filesystem support. Recognized amended instructions restore
  exact originals; intervening edits remain protected.
- **Changes missing:** save buffers before CLI reads, then Refresh. Watchers are
  hints; see [loading](loading.md). For stale UI builds, rebuild and reinstall the
  versioned artifact. Maintain one root npm lock, not nested lockfiles.

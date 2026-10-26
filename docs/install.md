# Install SpecSpec 0.1

Choose the global CLI, the VS Code extension, the desktop, or all three. This is one
source monorepo with independently usable products. Local builds do not publish
anything or install an extension into your editor automatically.

## Prerequisites

| Product | Runtime | Building from source |
| --- | --- | --- |
| CLI | Python 3.11+; Git for history, source anchors and comparisons | uv or pipx |
| VS Code | VS Code 1.90+, global CLI and Git in the workspace's environment | Node 22.12+, npm 10+ |
| Electron | Windows/Linux, global CLI and Git | Node 22.12+, npm 10+; developer Python for release archives |

The CLI does not need Node. Portable desktop archives include Electron, not Python
or Git. The extension includes its JavaScript/assets, not the CLI. Installation may
download build dependencies; application renderers use local bundled assets.

## Install the CLI globally

Use [uv tools](https://docs.astral.sh/uv/guides/tools/) or
[pipx](https://pipx.pypa.io/stable/installation/). These give you a `specspec`
executable across projects while isolating its Python dependencies. Do not install
it into each product's environment, use administrator privileges, or use `sudo pip`.

From a local checkout:

```sh
git clone https://github.com/jejay/specspec.git
cd specspec
uv tool install .
# Alternative:
# pipx install .
specspec --version
specspec --help
```

You can also install a checked-out source directory by absolute path, a Git URL or
the wheel built by `npm run package:cli` / `python -m build`:

```sh
uv tool install 'git+https://github.com/jejay/specspec.git'
uv tool install /path/to/specspec/dist/specspec-0.1.0-py3-none-any.whl
# Equivalent pipx inputs:
# pipx install 'git+https://github.com/jejay/specspec.git'
# pipx install /path/to/specspec/dist/specspec-0.1.0-py3-none-any.whl
```

Choose one installation source, not all of these invocations. A Git URL without a
ref follows the repository's current default branch, not an immutable release.
Append `@v0.1.0` only after that tag has actually been published. These instructions
do not assume a PyPI release or tell you to install an unrelated package with the
same name from an index. A source checkout is needed only to build the UIs, not
beside a wheel-installed CLI at runtime. `uvx --from /path/to/specspec specspec ...`
is available for occasional one-shot use; persistent installation is the normal setup.

### Make the command visible to your editor

If `specspec` is not found, run `uv tool update-shell` or `pipx ensurepath`, then
open a new terminal. **Fully quit and reopen VS Code/Electron** if they inherited
an older PATH. On Windows, `where.exe specspec` lists matching executables; on
Linux/macOS use `command -v specspec`. Check `specspec --version` in that same shell.

If an editor still cannot find it, configure an **absolute executable path**:

```json
{
  "specspec.command": "C:\\Users\\you\\.local\\bin\\specspec.exe",
  "specspec.args": []
}
```

Use your actual tool-bin path (`uv tool dir --bin` reports uv's). Settings are
machine-overridable: set them on the machine hosting the workspace, not in untrusted
project text. An alternative is an absolute Python interpreter that has SpecSpec
installed, with `specspec.args` set to `["-m", "specspec"]`.

Electron defaults to `specspec` on PATH too. Set trusted launch environment
`SPECSPEC_COMMAND` to its absolute executable and `SPECSPEC_ARGS` to `[]` when needed.
`--python` / `SPECSPEC_PYTHON` are developer alternatives, not a requirement to create
a per-project environment. See [desktop launch details](../electron/README.md).

## Install the VS Code extension locally

In the monorepo root:

```sh
npm ci
npm run package:vscode
code --install-extension dist/specspec-vscode-0.1.0.vsix
```

If the `code` shell command is unavailable, use VS Code's **Extensions → … → Install
from VSIX…**, choose that exact file and reload the window. Open your product folder,
trust it if appropriate, then run **SpecSpec: Open Graph**. Files under
`.specspec/` default to the graph custom editor. **Reopen Editor With → Text Editor**
retains access to ordinary Markdown.

No Marketplace account, personal access token, development host or F5 launch is
needed. The local publisher identifier `specspec-dev` is an extension identity,
not a claim that a Marketplace listing exists. The package contains compiled shared
code/assets/notices and no runtime npm installation is needed on the target editor.
[Extension guide](../vscode/README.md)

With SSH/tunnels, install the VSIX and CLI on the workspace host and keep Git beside
its real files. Follow [remote workspaces](remote-workspaces.md); browser-only virtual
filesystems are not supported. Remote execution has its own qualification scope.

## Run or package the desktop

From the monorepo root:

```sh
npm ci
npm run desktop
npm run desktop -- --project .
```

Choose one launch command. The first asks you to select and trust a project; the
second authorizes this checkout directly. Relative launch paths are relative to
the repository root for these root scripts. Do not supply untrusted executable or
project arguments. [Desktop guide](../electron/README.md)

For a portable build, set up and activate the [developer Python environment](../CONTRIBUTING.md),
then run `npm run package:electron`. Unpacked output is under `dist/desktop/`;
`dist/SpecSpec-0.1.0-win32-x64.zip` or the corresponding Linux `.tar.gz` is the
portable archive (architecture follows your Node runtime). Extract it as a whole,
keep its resources/licenses together and run `SpecSpec.exe` or `./SpecSpec`.
End users need the global CLI and Git, not Node/npm. Linux tar archives preserve
executable permissions. Keep Chromium's sandbox enabled; OS sandbox support is a
prerequisite. Builds are unsigned, without installers or auto-updates. Cross-building
is not platform qualification; Windows/Linux are the current desktop targets.

## Create and open a project

```sh
mkdir my-project
cd my-project
git init
specspec init -m "# Product purpose" -m "Explain the intended outcome."
specspec query --max-distance 2
```

`init` requires an existing directory and a nonempty manifesto. It creates
`.specspec/<id>.md` and a root `AGENTS.md` with the [shipped guide](agents.md), unless
that name is occupied. Existing files, directories and symlinks are preserved and
reported, not merged. Add `.specspec-local/` to your own `.gitignore`. SpecSpec does
not initialize Git, stage, commit or install hooks for you.

Now open the project in VS Code or select it in Electron. For a project without
Git, ordinary current reads/edits remain available; comparison availability is
reported explicitly. Node IDs are full and case-sensitive, including the final `=`.

## Upgrade and uninstall

Upgrade the CLI and UI packages together. From an updated checkout, reinstall the
CLI with `uv tool install --reinstall .` (or `pipx reinstall specspec` for its saved
source), rebuild the VSIX and reinstall it with `code --install-extension FILE --force`.
For a portable app, extract the new archive into a new directory; do not mix its
resources with an older package. Preserve project files and local draft/recovery
state. Check the changelog before replacing an early-version tool.

`uv tool uninstall specspec` or `pipx uninstall specspec` removes the CLI, not your
projects. Uninstall the VS Code extension through Extensions; delete an unpacked
portable app to remove its executable files. Neither action implies deleting your
specifications, Electron user-data drafts or `.specspec-local/` recovery records.

## Upgrading pre-release workspaces

0.1 uses **`.specspec/`**, replacing the development-only `_specspec/` location.
Before switching tools, finish or recover any interrupted transaction with the
matching old CLI and save unsaved editor drafts. Preserve experiments/backups.
Then explicitly rename the directory without changing node IDs or contents:

```sh
# Bash/Git Bash, from the product root; does not stage files:
mv -- _specspec .specspec
```

PowerShell equivalent: `Rename-Item -LiteralPath _specspec -NewName .specspec`.
Do not overwrite an existing destination. Update your own documentation/source path
references and editor setup, install matching 0.1 CLI/UI builds, and run
`specspec check --sources`. Review the resulting Git changes deliberately.

There is one current canonical location, not a fallback/dual reader or permanent
migration command. Current node fields and API remain 7. Historical trees with the
old directory may appear absent or be unavailable in current comparisons; renaming
the working tree does not rewrite your history. SpecSpec's maintained Gantt corpus
is independently reconstructed throughout; arbitrary user histories are not silently
rewritten and existing manual example clones are not reset.

## Troubleshooting

- **No project found:** create a graph in the right folder, or put `--root PROJECT`
  before the command. Discovery selects the nearest `.specspec` entry, even if invalid.
- **CLI failed to launch:** check PATH/version in the host's environment and the
  absolute executable setting. In VS Code, use **View → Output → SpecSpec**.
- **Graph invalid:** use `query --issues --with-ancestors`, `query ID --raw` and
  `diff --with-context`. Read the [repair guide](invalid-graphs.md); invalidity does
  not authorize deleting descendants or automatic changes to relationships.
- **Interrupted initialization/edit:** retain `.specspec-local/` and run
  `specspec --root PROJECT recover`. Do not remove its journal. Clear a stale lock
  with `--force-lock` only after confirming no writer is running. New instruction
  publication uses a same-filesystem exclusive link; filesystems that cannot create
  it report failure and retain recoverable state. Existing instructions are untouched.
- **Changes do not appear:** save editor buffers first for CLI reads. Use Refresh;
  filesystem watchers are hints. See [loading diagnostics](loading.md).
- **A VSIX/build looks stale:** run root `npm ci`, rebuild and reinstall the resulting
  versioned VSIX. There is one root npm lock; do not maintain nested lockfiles.

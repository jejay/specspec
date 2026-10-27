# specspec for VS Code

Connect your intentions, revisable choices and implementation in a Git-versioned
Markdown graph, inside your ordinary VS Code editor. Open a node's justification,
edit its binding text, compare revisions and follow source references without
turning the specification into a task board or an approval score.

**0.1 is an early local release. This extension is not on the Marketplace.**
[Product overview](https://github.com/jejay/specspec) ·
[Full installation guide](https://github.com/jejay/specspec/blob/main/docs/install.md)

## Install the CLI first

In a checkout of the monorepo, install the Python CLI globally:

```sh
uv tool install .
# Or: pipx install .
specspec --version
```

Python 3.11+ and Git are prerequisites. CLI dependencies are isolated; do not add
them to every product's runtime. Restart VS Code if its inherited PATH does not yet
include your tool-bin directory. A VSIX includes the extension/shared UI, not Python,
Git or a bundled CLI.

Opening a graph immediately checks CLI availability on the workspace host. A
blocking installation message and Retry action replace an unusable empty canvas;
the extension never installs Python packages automatically. Its package/display name
is **specspec-vscode**.

## Build and install the VSIX

Use Node 22.12+ and npm 10+. From the **monorepo root**, not `vscode/`:

```sh
npm ci
npm run package:vscode
code --install-extension dist/specspec-vscode-0.1.0.vsix
```

Without the `code` shell command, open VS Code's Extensions view, choose **… → Install
from VSIX…**, select that file and reload the window. No Marketplace credentials,
publication, global npm install or F5 development window is involved. To replace an
existing local build, reinstall that file with `--force` or use the same UI command.
The local identifier is `specspec-dev.specspec-vscode`.

## Open your graph

1. In a product directory, create a graph with `specspec init -m "# Product purpose"`
   if it does not already have one. This initializes Git when needed and creates
   or appends the packaged guide to `AGENTS.md`. Alternatively, use the graph's
   centered **Initialize specspec** form after opening an empty directory.
2. Open the folder in VS Code and trust it only if appropriate.
3. Run **specspec: Open Graph** from the Command Palette. Explorer's folder context
   menu also offers it. **specspec: Select Project** chooses another containing graph.
4. Open a `.specspec/<id>.md` file for its native node editor. Use **Reopen Editor
   With → Text Editor** for raw Markdown.

The graph opens in the main editor area. Split/file tabs share native document text
and retain independent cameras. File editing uses normal Save/autosave/undo/redo;
managed project actions require clean project documents. Historical views are
read-only. **specspec: Compare Revisions** opens a separate comparison panel; default
working views compare saved/native-overlaid content against fresh HEAD.

**Ctrl+S** (Command+S on macOS) saves through the current native or managed owner.
Shift-click node chrome toggles highlights; spotlights save IDs/messages locally
for agent discussion. The CLI remains available beside the visual editor.

## CLI settings and diagnostics

Default settings invoke `specspec` directly, without a shell. If PATH is unavailable,
set an absolute executable path in your own VS Code settings:

```json
{
  "specspec.command": "/absolute/path/to/specspec",
  "specspec.args": []
}
```

On Windows use a real executable path, with doubled backslashes in JSON. To run a
specific development Python, set its absolute path as `specspec.command` and
`["-m", "specspec"]` as `specspec.args`. Do not put an entire shell command into the
command string. Explicit machine-overridable settings take precedence over the
optional development `SPECSPEC_PYTHON` environment variable.

Errors and optional `specspec.traceLoading` diagnostics appear in **View → Output →
specspec**. File watchers are enabled; polling defaults to off
(`specspec.pollIntervalMs: 0`). Use Refresh when filesystem notifications are missed.
Invalid graphs remain inspectable/repairable; raw text is available for unreadable
nodes. No automatic repair, staging, commits or hook installation occurs.

SSH/tunnel workspaces run the adapter, CLI and Git on the workspace host. Install
the local VSIX there too. Virtual/browser-only filesystems are not supported.
[Remote setup and qualification](https://github.com/jejay/specspec/blob/main/docs/remote-workspaces.md)

## Development and boundaries

For source work, root `npm run build:vscode` compiles TypeScript and the shared
renderer. F5 remains an optional development workflow; see
[contributing](https://github.com/jejay/specspec/blob/main/CONTRIBUTING.md).

Local assets are bundled, project Markdown is rendered literally, and untrusted
workspaces cannot run the CLI. This is not a security certification or proof of
specification fulfillment. Large graphs are not virtualized; source symbols are
descriptive. The product is local-first and does not run a hosted coding agent.

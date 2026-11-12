# specspec graph editor

specspec keeps a project's specification as a graph of Markdown files, from the
owner's intentions through revisable conclusions to the implementation. This guide
covers the two graph editors: the VS Code extension (**specspec-vscode**) and the
standalone desktop app (**specspec-desktop**). Both draw the same canvas and run the
`specspec` command-line tool for every read and write.
[What specspec is and how it works with coding agents](https://github.com/jejay/specspec#readme)

## Install

1. Install the CLI (Python 3.11+ and Git): `uv tool install specspec` or
   `pipx install specspec`. Check it with `specspec --version`. If the command is
   missing, run `uv tool update-shell` or `pipx ensurepath` and restart the editor.
2. Download an editor from the
   [latest release](https://github.com/jejay/specspec/releases/latest):
   - **VS Code:** `specspec-vscode-<version>.vsix`. Install it with
     `code --install-extension specspec-vscode-<version>.vsix`, or use
     **Extensions → … → Install from VSIX…**, then reload the window.
   - **Desktop app:** `specspec-desktop-<version>-win32-x64.zip` for Windows or
     `specspec-desktop-<version>-linux-x64.tar.gz` for Linux. Unpack it and start
     `specspec-desktop.exe` or `specspec-desktop`. The Windows build is unsigned, so
     Windows may ask before its first start: **More info → Run anyway**.

The desktop app runs on Windows and Linux; on macOS, use the VS Code extension.

To build the editors from the repository instead (Node 22.12+ and npm 10+):

```sh
git clone https://github.com/jejay/specspec.git
cd specspec
npm ci
npm run package:vscode     # creates dist/specspec-vscode-<version>.vsix
npm run desktop            # starts the desktop app from source
```

`npm run package:electron` creates a portable desktop folder and archive in `dist/`.

## Open a project

- **VS Code:** open the project folder, trust it, and run **specspec: Open Graph**
  from the Command Palette (also in the Explorer context menu). **specspec: Select
  Project** opens a folder dialog to pick another project.
- **Desktop:** choose **Open project** (Ctrl+O) and confirm that you trust the
  folder, or start the app with `--project PATH` (from source:
  `npm run desktop -- --project PATH`).

A folder without a graph shows an **Initialize specspec** form: enter the
manifesto, the project's core goal. Initialization creates `.specspec/`, sets up Git
if needed and adds the agent guide to `AGENTS.md`. If the CLI is missing, the editor
shows installation steps and a **Retry** button.

## Read the canvas

The manifesto is the circle on the left; requirements are rounded cards and
implementation nodes square cards, with every relationship drawn from parent to
child. **Color by** switches between distance from the manifesto, node type,
influence and revision status; the legend names the current meaning.

- Zoom with the mouse wheel or the − / + buttons; drag the background to pan.
- **Frame graph** (Home or F) fits everything; **Actual size** (1) returns to 100%.
- **Frame rectangle**: hold Ctrl (Command on macOS) or click the icon, then drag
  around the area to fit. Escape cancels.
- Hovering a node emphasizes its relationships and darkens unrelated context.

## Edit

Select a node to edit its text, parents and sources in place; **Save node** or
Ctrl+S (Command+S) saves it. **+ New node** opens a form with the selected node as
its parent. If a
form has unsaved changes when you move on, the editor asks whether to discard or
keep editing. **Delete node** removes exactly that node's file; its children keep
their now-missing parent references until you reconnect or delete them.

In VS Code, `.specspec/<id>.md` files open in a node editor with normal Save, undo
and autosave; **Reopen Editor With → Text Editor** shows the raw Markdown. Graph
panels and the desktop app save through the CLI's protected writer, and
`specspec recover` repairs an interrupted write.

## Review changes

By default the canvas compares the working files with the last commit: added,
modified and deleted nodes carry A, M and D marks, and deleted nodes stay visible
until the deletion is committed. **Compare revisions** (in VS Code also **specspec:
Compare Revisions**) shows any two commits or a commit against the working files.

## Leave messages for your agent

Shift-click nodes to highlight them; Ctrl+Shift-click (Command+Shift-click) removes
one and **Clear highlight** removes all. **Create spotlight** saves the highlighted
nodes with a message and the current comparison. Your agent reads it with
`specspec spotlight show`; agents can leave spotlights for you the same way, and the
**Spotlights** menu lists them. Spotlights stay on your machine in
`.specspec/local/` until you flush them.

## Settings

- **VS Code:** `specspec.command` and `specspec.args` select the CLI (an absolute
  executable path, or a Python interpreter with `["-m", "specspec"]`).
  `specspec.pollIntervalMs` adds polling to file watching (0 disables it), and
  `specspec.traceLoading` writes load timings to **View → Output → specspec**.
- **Desktop:** `--python PATH`, or the environment variables `SPECSPEC_COMMAND` and
  `SPECSPEC_ARGS`, select the CLI; `--poll-interval-ms` enables polling. Drafts and
  view state are stored per project in the app's user-data directory.
- **Remote workspaces:** with VS Code Remote (SSH or tunnels), install the VSIX and
  the CLI on the remote host; the extension, CLI and Git run there.

Use the refresh button when a change made outside the editor does not appear. The
editors render project text literally and run the CLI only for trusted folders.

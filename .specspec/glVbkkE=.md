---
id: glVbkkE=
type: implementation
parents:
- F27DQ6w=
sources:
- path: tools/readme_screenshots.cjs
- path: docs/images/editor-vscode.png
- path: docs/images/editor-desktop.png
- path: README.md
---
# Capture both editors with a repository script

tools/readme_screenshots.cjs starts each editor in a disposable profile with a
loopback DevTools port and writes docs/images/editor-vscode.png and
docs/images/editor-desktop.png at twice the display resolution. README.md embeds both
after the concept sections.

VS Code runs the development extension on this repository with the default dark
theme, Git integration switched off and a native title bar, which stays outside the
captured page. The same file runs inside the extension host, where it opens the
graph, expands .specspec in the Explorer and clears startup notifications. The canvas
is colored by distance and framed as a whole.

The desktop app opens an independent clone of the Gantt example, compares
stage/02-code with stage/03-spec in revision colors, frames the deeper columns with
the rectangle tool and slides the graph until the top edge falls in a row gap.

The script needs built editors and, for VS Code, an installed VS Code that is free to
start a new window. It is run by hand; the test suites leave it out.

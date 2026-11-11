---
id: IkFelpQ=
type: implementation
parents:
- 3SfTeOo=
- fdB9ZLM=
- ALlkmT0=
sources:
- path: .github/workflows/ci.yml
- path: electron/launch.cjs
- path: electron/main.cjs
- path: package-lock.json
- path: electron/preload.cjs
- path: electron/renderer.js
- path: electron/scripts/build.cjs
- path: electron/security.cjs
- path: electron/store.cjs
- path: electron/test-host/run.cjs
- path: electron/test/launch.test.cjs
- path: electron/test/security.test.cjs
- path: electron/test/main.test.cjs
- path: electron/theme.css
- path: graph-ui-common/test-host/platform.cjs
- path: graph-ui-common/test-host/ui.cjs
---
# Host the shared graph in an Electron window that opens authorized local projects

`electron/main.cjs` selects and authorizes the project, takes the settings for launching the command line from the trusted launch options and the environment, creates and disposes the watchers and the session of a project, and serves the page and its assets through the local `specspec:` protocol. `electron/security.cjs` validates the sender and the content of every message and holds the fixed list of assets by which requests and navigation are confined. The preload script `electron/preload.cjs` runs sandboxed and isolated and exposes one fixed interface for messages and view state, and `electron/renderer.js` connects the shared renderer to it and adds the dialog for the two revisions of a comparison. The app runs without a menu bar and has the shortcut Ctrl+O or Command+O for choosing a project. System dialogs ask for the project directory, for trust in it and for the confirmation of a destructive action or of an overwrite.

`electron/launch.cjs` resolves an executable setting that contains a path against the directory the app was launched from, and the command line runs from a neutral working directory. `electron/store.cjs` keeps the presentation state and the drafts for each project, within limits of 3 MiB for one project and 32 MiB for the file, and protects a state file with corrupt bytes from being overwritten. It reads the file again when a project is opened, merges only the projects that this window changed when it saves, and repeats a failed write with the next update, so that several instances of the app keep each other's drafts. `electron/theme.css` defines the theme variables that the shared CSS reads, with the values of the Dark Modern theme of VS Code, among them the three Git colors for headlines and corner letters. `electron/scripts/build.cjs` builds the shared runtime into the app and copies the symbol, the launcher icon and the license of the project, and the license notices of the bundled libraries come with the shared build. `package-lock.json` pins the version of Electron.

The unit tests in `electron/test/launch.test.cjs`, `electron/test/main.test.cjs` and `electron/test/security.test.cjs` check the limits of launching, of stored state and of security. `electron/test-host/run.cjs` starts the built app with an isolated profile on a disposable checkout of the Gantt example and runs the harness of `graph-ui-common/test-host/ui.cjs` and `graph-ui-common/test-host/platform.cjs` in it. This run checks actual saves through the Python writer, a draft that is there again after a reload, the views of sources and of revisions, blocked requests, and what both graph editors share in canvas, paint and form. `.github/workflows/ci.yml` runs the unit tests and this run on Linux and Windows. At run time the app needs Python and Git, which are installed apart from it, and a trusted local launch with a project that the owner selects.

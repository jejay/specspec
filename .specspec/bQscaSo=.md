---
id: bQscaSo=
type: implementation
parents:
- ZacVi3g=
sources:
- path: graph-ui-common/src/binding-editor.js
- path: graph-ui-common/src/graph-vendor.js
- path: graph-ui-common/view.cjs
- path: graph-ui-common/media/graph.js
- path: graph-ui-common/media/graph-annotations.js
- path: graph-ui-common/media/graph.css
- path: graph-ui-common/package.json
- path: package-lock.json
- path: graph-ui-common/scripts/build.cjs
- path: graph-ui-common/test/binding-editor.test.cjs
- path: graph-ui-common/test/graph.test.cjs
- path: graph-ui-common/test-host/inline.cjs
- path: graph-ui-common/test-host/ui.cjs
- path: graph-ui-common/test-host/platform.cjs
---
# Wrap the merge view of CodeMirror as the shared text field with inline changes

`graph-ui-common/src/binding-editor.js` bundles the state, view, commands and merge packages of CodeMirror behind the interface that the text field of the form needs: a value, a selection and permissions. The renderer passes the base of the current comparison to it, also while the form holds unsaved changes. The blocks of original text, the inserted lines, the character highlights and the gutters are derived from that base and from the editable text. The local assets and the license notices are built into the outputs of both editors. The shared CSS in `graph-ui-common/media/graph.css` uses the theme tokens for diffs with fallback colors for the standalone app, contrast borders and a resizable field within the 822px content width of the expanded card.

Loading text by program and updating the comparison are kept apart from input: an edit by the user sends the form, with the current text alone, through the guarded session. Moving to another node resets the local history. The form of a VS Code document has no local history, so that VS Code owns undo and redo, and the forms of graph panels and of the desktop app keep a local history. The forms of comparisons between commits and of invalid or deleted nodes keep their restrictions on selecting and saving.

The unit tests in `graph-ui-common/test/binding-editor.test.cjs` cover literal removed and inserted content, the separation of input from programmatic changes, the refresh of a comparison, text cursor and focus, the ownership of the history, the forms of added, deleted and unchanged nodes, and permissions. The renderer tests in `graph-ui-common/test/graph.test.cjs` cover the lifecycle of a form that keeps its input. Complete runs in the installed desktop app and the installed VS Code extension on Windows verify actual typing in the editable field, the painted diff colors, a refresh with draft and text cursor, the fit of 80 columns, the geometry of the resizable field, saves through the writer, reloads and, for VS Code documents, unsaved state, save, undo, split views, raw edits and repair. These runs use the independent Gantt history in the current node format and small fixtures for VS Code documents, and other platforms are outside them.

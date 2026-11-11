---
id: znpy2MA=
type: implementation
parents:
- iHpAyAE=
sources:
- path: graph-ui-common/view.cjs
- path: graph-ui-common/media/graph.js
- path: graph-ui-common/media/graph-model.js
- path: graph-ui-common/media/graph-annotations.js
- path: graph-ui-common/host/session.cjs
- path: graph-ui-common/host/cli.cjs
- path: graph-ui-common/host/project.cjs
- path: graph-ui-common/host/git-watch.cjs
- path: vscode/src/extension.ts
- path: vscode/package.json
- path: electron/store.cjs
- path: tools/rainbow-playground/index.html
- path: tools/rainbow-playground/app.js
- path: graph-ui-common/test/graph.test.cjs
- path: graph-ui-common/test/session.test.cjs
- path: graph-ui-common/test/playground.test.cjs
- path: vscode/test/bridge.test.cjs
- path: graph-ui-common/test-host/platform.cjs
---
# Word labels, tooltips and status texts concisely in the graph, the dialogs and the playground

The shared shell in `graph-ui-common/view.cjs` gives the canvas to the graph, to a floating navigation control and to short color swatches and gradient ends. The labels and tooltips that the tool writes state current roles, actions and steps of repair. The source controls carry short labels for the kind of tracking, and the documentation explains them in full. The entry of a spotlight states its number of nodes and, once it is applied, how many of them are absent, and the Spotlights button says when its list is out of date. Errors of the bridge between an editor and the command line keep their meaning for failure and recovery and say directly what to do. The palette playground in `tools/rainbow-playground` describes its controls and its exports in positive words.

DOM tests check the short legends and the names of icons together with literal project Markdown and literal diagnostics. The tests of VS Code documents, of the session, of the bridge and of the playground assert their safety conditions and check the current labels of actions and states. The four influence choices, linear and logarithmic, and the independent cues for Git and for highlights are all available.

Probes in the installed editors with invalid files check that current structural findings appear and that input is kept. A node whose file cannot be read cannot be saved through the writer. The repair form of a VS Code document keeps an actually empty body and partly typed source input, whether or not the document counts as a node of the graph. The tests of poll coalescing hold a read at an explicit barrier and verify one follow-up, whatever the throughput of the machine.

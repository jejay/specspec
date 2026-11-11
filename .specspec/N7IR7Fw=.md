---
id: N7IR7Fw=
type: implementation
parents:
- uY3KPsM=
- KGvVHh0=
- VDss3KM=
- FJj-9xY=
sources:
- path: vscode/package.json
- path: vscode/src/extension.ts
- path: graph-ui-common/host/documents.cjs
- path: graph-ui-common/host/session.cjs
- path: graph-ui-common/host/cli.cjs
- path: graph-ui-common/media/graph.js
- path: graph-ui-common/test/loading.test.cjs
- path: vscode/test/extension.test.cjs
- path: vscode/test/bridge.test.cjs
- path: vscode/test-host/remote.cjs
- path: graph-ui-common/host/reads.cjs
- path: graph-ui-common/host/wire.cjs
- path: graph-ui-common/test/wire.test.cjs
- path: electron/main.cjs
---
# Run on the workspace host and deliver the working graph before its comparison

`vscode/package.json` declares that the extension runs on the workspace host, that it needs a real file system and that loading diagnostics are opt-in. The adapter in `vscode/src/extension.ts` uses files of the host as resources, the executable settings of the remote machine, the asset addresses and messages of VS Code and saving by VS Code. `ProjectReads` in `graph-ui-common/host/reads.cjs` shares identical reads in flight in the desktop app and in VS Code: it compares the stamps of documents and generation before and after a read, gives each view its own copy of the result and passes hints about the base of the comparison, which are limited in size and verified. `ProjectDocuments` in `graph-ui-common/host/documents.cjs` adds the planning of edits to editor documents and the coordination of their saving. The first read of a node-file editor supplies the initial usable graph while the wiring of the editor completes asynchronously. `GraphSession` in `graph-ui-common/host/session.cjs` first draws the working graph, explicitly marked as provisional, and then a fresh comparison; a comparison between commits shows its selected revisions read-only. The renderer in `graph-ui-common/media/graph.js` keeps drafts, text cursor and camera and restricts the project controls while the graph is provisional. The loading records measure the phases in the host process and the drawing in the client, each with its own clock.

When the command-line process fails after a change has started, the error explains that the outcome is unconfirmed and asks to inspect the current state, and no action is repeated automatically. The regression tests of adapter and session cover races of shared and first reads, delayed comparisons, disposal, trust, the boundaries of resources, bound editor documents and lost replies. The opt-in module `vscode/test-host/remote.cjs` checks on a disposable clone of the history that execution is actually placed on the workspace host, that open documents are overlaid, which nodes are rendered and that source objects resolve. The qualification of a transport is reported for each dispatched run separately.

The project reads mark a result as superseded when the generation or the document stamp changed, apart from a closed project and from a validation failure. The session keeps the current presentation during the limited attempts and coalesces one fresh automatic refresh, driven by an event, after repeated supersession. A read of the working files that the owner requested ends with an error that says to retry and with a follow-up. A graph that is actually invalid gets the marked repair state, and a change through the writer begins with a fresh read. `graph-ui-common/test/loading.test.cjs` covers repeated races of generation and text, repair, requested reads and cancellation on disposal, with polling off and the deadlines at their length.

One API channel per project keeps its interpreter running across requests, every request is validated afresh, and source previews use a channel of their own. The first read of a node-file editor is retried when it is superseded, before the editor is attached, and the fallback is reported without making the wiring of the editor wait for an answer to a notification. A project in the host process disposes the API channels it owns.

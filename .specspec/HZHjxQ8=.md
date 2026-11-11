---
id: HZHjxQ8=
type: implementation
parents:
- TpFMeZc=
- 0aNDHfQ=
- yEoFkOE=
- sxxzsrk=
sources:
- path: graph-ui-common/host/session.cjs
- path: graph-ui-common/host/git-watch.cjs
- path: graph-ui-common/media/graph.js
- path: graph-ui-common/test/session.test.cjs
- path: graph-ui-common/test/graph.test.cjs
- path: graph-ui-common/test/loading.test.cjs
- path: graph-ui-common/test-host/ui.cjs
- path: graph-ui-common/test-host/platform.cjs
- path: vscode/test-host/run.cjs
- path: electron/test-host/run.cjs
- path: graph-ui-common/test/git-watch.test.cjs
- path: vscode/src/extension.ts
- path: vscode/test/extension.test.cjs
- path: graph-ui-common/host/client.cjs
- path: graph-ui-common/host/reads.cjs
- path: graph-ui-common/test/client.test.cjs
- path: src/specspec/api_transport.py
- path: src/specspec/cli.py
- path: tests/test_api_transport.py
- path: vscode/src/bridge.ts
- path: electron/main.cjs
---
# Schedule source previews, spotlight reads and Git watching apart from graph reads

`GraphSession` in `graph-ui-common/host/session.cjs` gives source previews a lane of their own that only reads and that coalesces requests: one runs and the latest one waits. A preview is bound to the commits of the comparison on display, and a reply that the view has moved past is dropped. Automatic graph reads and the notifications of the spotlight store have separate refresh work. An explicit Refresh, the first load and polling read the spotlight list as well, which recovers the list after an error and sets the baseline for counting arrivals.

`GitWatcher` in `graph-ui-common/host/git-watch.cjs` finds the private and the common Git directory with an asynchronous Git call that runs without a shell and within limits of 3 seconds and 64 KiB of output. It coalesces notifications, reconciles its watches with the directories it found and adopts no result after it was closed. The adapters of VS Code and of the desktop app both use this watcher for HEAD and the refs, and each watches the node files separately. A write to the stat cache of the index and a status event of the Git extension of VS Code leave the displayed comparison of HEAD and working files as it is, and an explicit operation on staged content reads the index at that moment.

`CliClient` in `graph-ui-common/host/client.cjs` keeps the channels of a project: it reuses an interpreter across requests, runs source previews on a channel of their own, queues at most 32 requests per channel and limits a request and its reply to 16 MiB each and, by default, to 120 seconds. Every request reads the current state, and disposal and failure are guarded as the channels require. `api_transport.py` serves `api --stream`: an unexpected failure answers its frame with an `INTERNAL` envelope, and the channel goes on serving.

The tests of the session, the renderer and the watcher in `graph-ui-common/test` hold background work open while they exercise the races between the latest request and navigation, and they check that writes and editor documents keep their owners. The suites in the installed VS Code and desktop app exercise source previews, the canvas, spotlights sent in both directions, the recovery of the watchers, the life cycle of editor documents, and a reload and a switch of revisions with stored state.

The tests of the VS Code adapter that count reads exactly keep the first Git discovery pending until the test ends. This makes the counts for a bootstrap with stable input, for the watcher of the node files and for spotlight events exact, while the default fixtures run against real Git. Separate tests cover a discovery hint that is valid and arrives late together with the graph refresh it causes, and a bootstrap of an editor document that is blocked and needs a fresh read once its context is invalid.

# Shared graph UI

One host-neutral implementation of the native DOM/SVG canvas. `media/` contains
the renderer, camera and presentation model; `view.cjs` supplies the safe local
HTML shell; `host/session.cjs` serializes API-6 operations/render handshakes;
`host/cli.cjs` bounds shell-free Python processes. Python still validates and mutates
canonical data. No host SDK is imported by these files. `host/documents.cjs`
provides portable project-level document coordination and minimal text edits;
per-view sessions optionally use a native-document port rather than CLI saves.

Renderer adapters supply `window.SpecSpecHost` with `getState`, `setState`,
`postMessage`, and `onMessage`. Host sessions supply CLI invocation, authorization,
confirmation, revision selection, posting/logging, and the shared `renderMatches`
and `sameNode` contracts. Watchers call `scheduleRefresh`; `configurePolling(ms)`
sets an optional interval (0/default disables polling). Disposal releases timers,
retries and render waits. `host/watch.cjs` supplies non-recursive Electron directory
watching with parent-directory reattachment; VS Code uses its filesystem API.
Events are reload hints, not an exact change log. Invalid reloads retain the last
valid view marked out of date; valid data is compared directly, without hashes.
Superseded generation/text reads retry through the coalesced event queue without
classifying the files as invalid. Each refresh has bounded attempts; disposal
cancels follow-up work, and actual invalid reads retain their repair restrictions.
`host/annotations.cjs` watches the checkout-local immutable spotlight store independently,
including while a revision graph is open. `media/graph-annotations.js` owns the retained
dropdown, round red arrival-count badge and editable camera-scaled white rings.
Shift-click toggles IDs and Ctrl/Command+Shift clears one member, identically for
manual and spotlight-applied highlights. Change --spotlight-color in media/graph.css
to try another ink. A local message dialog sends IDs/message to the guarded creation
API; the adapter supplies current comparison and native buffers without invoking
Save. Selection closes the menu, switches comparison, then frames available target/
deleted-base nodes, retaining drafts. Sparse workspace drift warns without hiding rings. Existing initial entries establish a zero-count baseline; opening resets
new arrivals, and reload starts a new in-memory count. Python owns immutable storage
and metadata-only comparison records, shared by the CLI and both hosts. Dropdown/highlight preferences
are per view; unread counts are not persisted. Internal paths/transport names remain
independent of public Spotlights naming. Neutral curve/head ink darkens from 70% at
70% zoom and above to 35% at 16% and below; diff and hover inks stay distinct.
Node fills transition separately from their exact actual-size 15%/24% tints at 40%
zoom toward painted borders at 16% and below, including contrast themes and hovered
borders. The rounded floating HUD keeps the full canvas available.
Its rectangle tool captures a one-shot primary-pointer drag, latched through
Ctrl/Command release, with cancellation and native/highlight event boundaries.
Legends pair colors with concise labels; tutorial text lives in the
[canvas guide](../docs/node-canvas.md#canvas-controls).
See [spotlight semantics](../docs/spotlights.md).

The eight Color by modes include continuous Absolute influence, Relative influence,
Log Absolute Influence and Log Relative Influence. All count unique all-depth
descendants; absolute uses zero to the non-root maximum, relative uses cohort
minimum/maximum at equal longest distance. Log modes transform raw counts with
`log1p` before normalization, and linear modes remain available. The shared model
lazily caches each revision's raw domains for all four choices. A warm green/yellow/red sRGB ramp and gradient
legend stay separate from the exact seven-color distance/type/status table. Full
target/base context survives focus, and ties use green while the manifesto stays gray.

State must be project-scoped and per-view when a host supports multiple tabs. A host must not expose arbitrary CLI or filesystem
operations to project content. Future agent integration is a seam, not an implemented
Claude Code/Codex connector.

```sh
npm --prefix graph-ui-common ci
npm --prefix graph-ui-common test
```

`buildGraph(mediaDir, runtimeDir)` generates pinned offline vendor assets/license
notices and copies runtime sources into a host's output. Generated copies aren't
hand-edited or canonical sources. Both hosts build the exact same renderer bytes.
Native draft DOM/caret, original node records, revision metrics, layout/hover/camera
and safe literal project text are covered by the migrated regression suite.
VS Code node-file edits use Python's non-writing `api` planning operation and native text buffers;
Electron retains managed saves. Shared document tests cover planning, coalescing,
sequence acknowledgements, version/text conflicts and UTF-16/CRLF-safe edits. See
[document/persistence semantics](../docs/native-editors.md).

`test-host/budgets.cjs` supplies the installed suites' aggregate phase allowances;
individual and production deadlines remain independent. The shared CDP harness
fails closed transports promptly and foregrounds even when optional window sizing
is unavailable. [Installed-host verification](../docs/investigations/host-smoke.md)
describes complete Electron/VS Code coverage and controlled causal regressions.
`host/client.cjs` reuses bounded per-project API processes, with an independent
preview channel and fresh backend reads for every frame. `host/git-watch.cjs`
coalesces asynchronous HEAD/ref discovery; canonical and Spotlight notifications
retain independent paths. Ordinary CLI commands keep the one-shot bridge.
`test/camera.test.cjs` isolates rectangle state/inversion and synthetic Mac mapping;
`test-host/canvas.cjs` runs early in each installed suite to inspect computed paint,
floating chrome, real pointer capture/outside release and native editing.

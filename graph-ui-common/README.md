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
dropdown, round red arrival-count badge and editable multicolor 8px rings.
Shift-click cycles colors and Ctrl/Command+Shift clears one member, identically
for manual and spotlight-applied highlights. A local message dialog sends exact
references to the guarded session's creation API; the VS Code adapter supplies
actual native buffers without invoking Save. Immutable records are then available
through spotlight show for owner-to-agent messages. Selection closes the menu and frames the matching union in the full canvas,
retaining drafts. Existing initial entries establish a zero-count baseline; opening resets
new arrivals, and reload starts a new in-memory count. Python owns immutable storage
and exact blob metadata, shared by the CLI and both hosts. Dropdown/highlight preferences
are per view; unread counts are not persisted. Internal paths/transport names remain
independent of public Spotlights naming. Neutral curve/head ink darkens continuously
from 70% at actual size to 35% at minimum zoom; diff and hover inks stay distinct.
See [spotlight semantics](../docs/spotlights.md).

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
is unavailable. [The Windows smoke investigation](../docs/investigations/host-smoke.md)
records complete Electron/VS Code results, scope and diagnostic limits.

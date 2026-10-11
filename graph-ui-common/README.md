# Shared graph UI

One host-neutral implementation of the native DOM/SVG canvas. `media/` contains
the renderer, camera and presentation model; `view.cjs` supplies the safe local
HTML shell; `host/session.cjs` serializes API-3 operations/render handshakes;
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
VS Code node-file edits use Python's non-writing `editor` API and native text buffers;
Electron retains managed saves. Shared document tests cover planning, coalescing,
sequence acknowledgements, version/text conflicts and UTF-16/CRLF-safe edits. See
[document/persistence semantics](../docs/native-editors.md).

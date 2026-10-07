# Shared graph UI

One host-neutral implementation of the native DOM/SVG canvas. `media/` contains
the renderer, camera and presentation model; `view.cjs` supplies the safe local
HTML shell; `host/session.cjs` serializes guarded API-2 operations/render handshakes;
`host/cli.cjs` bounds shell-free Python processes. Python still validates and mutates
canonical data. No host SDK is imported by these files.

Renderer adapters supply `window.SpecSpecHost` with `getState`, `setState`,
`postMessage`, and `onMessage`. Host sessions supply CLI invocation, authorization,
confirmation, revision selection, posting/logging, and the shared `renderMatches`
contract. Watchers call `scheduleRefresh`; disposal releases timers/render waits.
State must be project-scoped. A host must not expose arbitrary CLI or filesystem
operations to project content. Future agent integration is a seam, not an implemented
Claude Code/Codex connector.

```sh
npm --prefix graph-ui-common ci
npm --prefix graph-ui-common test
```

`buildGraph(mediaDir, runtimeDir)` generates pinned offline vendor assets/license
notices and copies runtime sources into a host's output. Generated copies aren't
hand-edited or canonical sources. Both hosts build the exact same renderer bytes.
Native draft DOM/caret, original fingerprints, revision metrics, layout/hover/camera
and safe literal project text are covered by the migrated regression suite.

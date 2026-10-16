---
id: JTezmL0=
type: implementation
parents:
- E7O_6GU=
- rvz48KY=
- RY5LFw8=
sources:
- path: graph-ui-common/media/graph-model.js
  blob: 7e9e35d891231a16e72a356cb83b32dc5f456cf0
  mode: strict
  ranges:
  - - 231
    - 231
  - - 325
    - 333
  - - 345
    - 354
- path: docs/own-spec.md
- path: docs/spotlights.md
- path: electron/main.cjs
- path: electron/security.cjs
- path: electron/test-host/run.cjs
- path: electron/test/security.test.cjs
- path: graph-ui-common/host/annotations.cjs
- path: graph-ui-common/host/session.cjs
- path: graph-ui-common/media/graph-annotations.js
- path: graph-ui-common/media/graph.css
- path: graph-ui-common/media/graph.js
- path: graph-ui-common/test-host/platform.cjs
- path: graph-ui-common/test-host/ui.cjs
- path: graph-ui-common/test/annotations.test.cjs
- path: graph-ui-common/test/graph.test.cjs
- path: graph-ui-common/test/session.test.cjs
- path: graph-ui-common/view.cjs
- path: vscode/src/extension.ts
- path: vscode/test/extension.test.cjs
---
# Render a spotlight dropdown with whole-record rings and framing

The shared renderer integrates immutable checkout-local spotlights into a compact
newest-first dropdown anchored below the Spotlights button. Each text-only entry
represents a whole shot and its shared message, with time and version counts.
Existing retained records with different group texts display those texts together.
Selecting a shot replaces highlights with its exact members and colors, closes the
dropdown and frames their union using the existing camera frame operation over the
full canvas. Repeated selection frames again. Explicit clear removes rings.
Focused drafts survive the transition to overview. Compact status counts replace
member/detail/preview UI. The dropdown supports keyboard navigation, Escape,
outside dismissal, viewport clamping and scrolling. Native node menus stay usable.

A round red toolbar badge counts one per new shot since dropdown opening, starting
with a zero-count baseline. Counts/New cues stay in renderer memory. Arrivals
preserve editing focus/caret, camera, selection, dropdown choice and older
entries. A version-aware editable highlight map and dropdown choice remain per-
view preferences. Exact members paint an equal-inset outline with width
`max(5, 3 / k)` world units at camera scale `k`; its negative offset keeps the
ring inside the unchanged card outline. This gives a 5-unit actual-size width and
a 3 CSS-pixel minimum when zoomed out, using the same compensation logic as the
connection stroke with a ring-specific pixel floor. It remains separate from
keyboard focus and fills. Flush uses host confirmation and a locked reviewed-list
check.

The shared session reads spotlights independently of graph validity and historical
selection. Ready/reload republishes retained entries for a new baseline. Directory
watching serves both hosts; polling and Refresh remain fallbacks. Adapters retain
trust, action/asset allowlists and disposal boundaries. Shared DOM tests cover
multicolor whole-shot selection, full-width framing, keyboard/outside dismissal,
baselines/counts, retained drafts, errors and flush. Real-host probes add records
through spotlight add and inspect arrival/ring paint, framing and native menus.

Verification covers exact-version rings, backchannel messages, immutable retained
records, drafts, caret and camera through shared unit tests and installed probes.
The common installed harness includes compact/circular/expanded backchannels,
cascade ghosts, file recovery and native document lifecycle checks.
docs/investigations/host-smoke.md describes complete installed verification.
Command/Meta+Shift has synthetic-event coverage; physical macOS qualification
retains its own evidence boundary.

The shared renderer handles Shift-click cycling and Ctrl/Command+Shift removal
on node chrome, whole-set clear and a message dialog for immutable spotlight
creation. The guarded shared session supplies view revisions and native overlays
to the backend, and both adapters authorize the new creation action.

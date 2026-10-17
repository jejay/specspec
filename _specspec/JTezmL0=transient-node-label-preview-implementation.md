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
- path: graph-ui-common/test-host/canvas.cjs
---
# Render white identity highlights and switch spotlight comparisons

The shared renderer uses one --spotlight-color CSS variable, initially white, for
manual and spotlight-applied rings. Shift-click toggles IDs; Ctrl/Command+Shift
removes them. Outline width max(5, 3 / k) and negative offset preserve camera-scaled
inset geometry and independent focus/semantic/Git paint. A message modal captures
IDs and current comparison through the authorized shared session.

The newest-first dropdown retains arrival badges, keyboard/outside dismissal and
window clamping. Selecting a record delegates its comparison switch to the shared
session, applies all IDs and frames available nodes only after the comparison is
displayed. Deleted base nodes and drifted workspace versions remain highlightable;
missing IDs remain selected. Workspace warnings remain visible outside the menu.
Drafts, native input and camera survive arrivals and creation. Explicit comparison
navigation releases the active spotlight context while keeping editable IDs.

Shared renderer/session and host-adapter tests cover one-ink toggle/clear/compose,
comparison switching before framing, best-effort drift/missing highlights, fresh
HEAD warnings, arrivals/baselines, historical views, authorization, errors and
reviewed flush. Installed-host probes use the color-free CLI and metadata-only
backchannel. Their platform and filesystem evidence remains bounded; physical
macOS modifier qualification retains its separate evidence boundary.

Complete Windows host probes verify live advisory drift with persistent rings,
real added/deleted historical comparison selection, retained managed drafts,
metadata-only agent readback and reload baselines. Paint probes use the current
40%-to-16% fill schedule and camera-scaled ring dimensions.

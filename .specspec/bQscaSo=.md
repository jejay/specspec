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
# Render and verify shared editable inline node comparisons

The shared binding-editor module bundles CodeMirror state/view/commands/merge
behind the binding control's value, selection and permissions interface. The
renderer supplies the current comparison base even while retaining a dirty form.
Original-text blocks, inserted lines, character highlights and gutters are derived
from that base and the editable target. Local assets and license notices are built
into both host outputs. Shared CSS uses diff theme tokens, standalone fallbacks,
contrast borders and the existing resizable 822px editor content budget.

Programmatic loads and comparison updates stay distinct from input notifications;
user transactions send target-only forms through the existing guarded session.
Changing resources resets local history. Native document forms omit local history
so the host owns undo/redo. Managed forms retain local history. Historical and
invalid/deleted forms keep their established selection and save restrictions.

Shared unit tests cover literal removed/inserted content, input separation,
comparison refresh, caret/focus, history ownership, added/deleted/plain forms and
permissions. Renderer tests cover retained form lifecycle. Complete installed
Windows Electron and VS Code runs verify actual contenteditable typing, diff theme
paint, draft/caret refresh, 80-column fit, resizable root geometry, managed saves,
reloads and native dirty/save/undo/split/raw-edit/repair lifecycle. These runs use
independent current-schema Gantt history and bounded native fixtures; other host
platforms retain their separate qualification boundary.

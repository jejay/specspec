---
id: JTezmL0=
type: implementation
parents:
- E7O_6GU=
sources:
- path: graph-ui-common/media/graph.js
- path: graph-ui-common/media/graph.css
- path: graph-ui-common/view.cjs
- path: graph-ui-common/test/graph.test.cjs
- path: graph-ui-common/test-host/ui.cjs
- path: docs/own-spec.md
---
# Render ephemeral right-click label rings

Renderer-local `previewLabels` entries drive the exact none/red/blue/green/purple/
turquoise/yellow cycle on card chrome. Same-view redraw/focus/mode/Refresh reapplies
them; new views and new draft previews initialize empty. Native fields, links,
buttons and background retain normal menus.

CSS paints a 6px inset outline at -6px offset plus an independent focus cue. Labels
retain their hue on hover and follow unrelated darkening. Accessible preview-only
text identifies the state. Tests verify equal ring paint, native-menu boundaries,
cycle/reset, zero persisted entries/messages and stable forms/caret/camera/routes.

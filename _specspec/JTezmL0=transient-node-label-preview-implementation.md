---
id: JTezmL0=
type: implementation
parents:
- E7O_6GU=
sources:
- path: graph-ui-common/media/graph.js
  symbol: previewLabels, labelCycle, applyPreviewLabel, labelIdFor and contextmenu
- path: graph-ui-common/media/graph.css
  symbol: data-preview-label inset outline and focus cue
- path: graph-ui-common/view.cjs
  symbol: preview-only footer caveat
- path: graph-ui-common/test/graph.test.cjs
  symbol: five label state/native menu/geometry/CSS regressions
- path: graph-ui-common/test-host/ui.cjs
  symbol: checkLabelPreview and focused screenshot filter
- path: docs/own-spec.md
  symbol: temporary label visualization
---
# Render a temporary right-click label ring without persisting labels

Implement DG-JpDc= through E7O_6GU= in the shared graph renderer/template/CSS.
Use renderer-local Map entries by node ID; new views start empty, same-view
redraw/focus/mode/Refresh reapplies them and new draft creation clears its preview.
Orphaned drafts use their original selected-node key. No entries are serialized
into drafts, host.setState, messages, canonical records, CLI or filesystem.

Delegate contextmenu on card chrome/headlines and cycle none/red/blue/green/purple/
turquoise/yellow/none. Fixed trial inks are independent of palette/Git meanings.
Preserve native menus for inputs, textarea, selects, editable content, links and
inner buttons and leave background menus untouched. Do not select/edit/focus a
node on label click. Read-only/removed/root/draft cards support presentation labels.
Add data-preview-label/custom ink and accessible preview-only descriptions. Clear
both when cycling back to none. UI footer and docs explicitly warn not saved;
persistence will likely be explored later, not implemented in this slice.

CSS uses a 6px solid outline at -6px offset, equal around the existing border box,
covering ordinary border paint without changing border widths, forms/size or ports.
A separate box-shadow focus cue remains available. Hover cannot replace the label
outline; unrelated-card brightness darkening still applies. Base semantic/Git/
withdrawal styling is untouched and reappears when the label is cleared.

Five new unit regressions verify exact cycle/order and per-ID independence, zero
state/message/record changes, geometry/camera/path invariance, redraw/refresh/mode/
focus retention and new-renderer reset, expanded native draft/caret and context
menu exceptions, root/read-only/removed/new-draft cases and uniform inset CSS.
All 127 common (including seven playground tests), 34 VS Code adapter, nine Electron
and 111 Python tests passed, with Ruff lint/format and both working validators.

The complete real Windows Electron and VS Code host suites ultimately passed via
explicit rebuild/compile followed by direct Node host runners. Actual contextmenu
cycling checked compact/root/expanded cards, every color, same-color outline under
hover, zero persisted host-state changes and unchanged geometry/camera/edge paths.
Label screenshots from the final Electron direct run were inspected. Native-menu
probes distinguish this renderer's cancellation from VS Code's document-level menu
handler; they suppress synthetic host menus only inside the test, not production.
An initial raw defaultPrevented assertion misclassified VS Code's own handler as a
renderer interception; the focused probe now checks the actual listener boundary.

Retain initial failed attempts: several npm-launched Electron runs stalled at the
existing camera-reset restoration check before label assertions. One diagnostic
run reached label checks and exposed Chromium/host zoom rounding: a CSS 6px outline
computed as 5.6px. Compare with an independent 6px browser probe under the same
host zoom, preserving the declared-width contract rather than expecting impossible
unquantized paint. Temporary diagnostic logging and baseline generated-asset swaps
were removed/restored by the final build. No production camera code, camera/routing
assertion or timeout was weakened. Direct runs with current assets passed twice;
no definitive root cause for the launch/timing failures is claimed. An optional
SPECSPEC_SCREENSHOT_FILTER captures selected names without skipping any tests.

Both hosts used independent disposable maintained-history clones. Existing native
save/undo/redo/split/CRLF/Unicode, watcher/invalid-file recovery, sandbox, actual save,
draft reload and historical switching checks remain passing in the successful runs.
Ignored logs/screenshots are bounded local evidence. Current tests ran against a
worktree with unrelated pre-existing fixture/history/workspace-policy edits; those
are not staged with this slice. Update README, conclusion/canvas/own-spec docs and
validate the exact index before the separate commit. No hook or schema change,
Gantt-history rewrite, approval signal, backend label API or persistence promise.
Other platforms, every display/theme, full manual menu/accessibility and large-graph
behavior remain unverified; trial inks/outline thickness are revisable choices.

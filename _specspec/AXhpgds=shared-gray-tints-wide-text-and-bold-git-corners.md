---
id: AXhpgds=
type: implementation
parents:
- xCOHepQ=
sources:
- path: graph-ui-common/media/graph.css
  symbol: shared card hover tints/borders, monospace text and git-corner
- path: graph-ui-common/media/graph-model.js
  symbol: DETAIL_WIDTH
- path: graph-ui-common/media/graph.js
  symbol: updateHoverAppearance
- path: graph-ui-common/test/graph.test.cjs
  symbol: shared hover state, width and CSS regressions
- path: graph-ui-common/test-host/ui.cjs
  symbol: checkHover, gray tint/theme probes and 80-column text fitting
- path: graph-ui-common/test-host/platform.cjs
  symbol: actual 20px/800 Git corner size, bounds and no collisions
- path: vscode/test-host/run.cjs
  symbol: installed shared canvas and native document checks
- path: electron/test-host/run.cjs
  symbol: installed shared canvas and desktop checks
---
## Later node-shape revision

Dn6Ult8= requests sharper implementations, slightly rounder requirements and a
full-circle manifesto. AZbsoEA= chooses type radii and a content-fitting circular
editor. Original all-card dimensions and actual checks below remain historical;
ordinary cards retain those sizes and only the manifesto gets a circular outline.
The native form content budget, palette, text and Git/hover behavior are unchanged.

## Later hover-scope correction

The all-card white borders and tests below describe the c2d8e15 implementation,
not a user request or current contract. pqNhV6s= clarifies white only for
the manifesto; bLBNk80= supersedes white borders elsewhere and washed-out
colored-link emphasis. Earlier test counts remain historical evidence.

# Share gray card styling, fit typical 80-column text and strengthen Git markers

The user's correction rejects the previous solid pale manifesto as a mistaken
interpretation, not an approved design. Retain that evidence explicitly as
superseded history. Keep its #d3d3d3 semantic accent/legend, but remove root-only
solid fills, dark text, badge backing and contrast-theme background exceptions.
All types now use shared theme text and tint rules, including expanded cards.
At rest ordinary themes mix 15% accent into the canvas; hover uses 24% and a white
border without changing border width. Contrast-theme resting styles stay shared.
updateHoverAppearance adds node-hovered to just the actual hovered card, reusing
existing delegated transitions/reconciliation so forms and camera motion work too.
The same class drives testable transient paint; exit/blur/touch/redraw remove stale
state. One-hop relationship emphasis and unrelated-context darkening are unchanged.

Expanded width is 860 world units, up from 620; compact cards stay 264 by 112.
The initial 820-unit candidate was increased to leave padding/scrollbar margin at
representative 16px editor fonts. textarea and pre share the host monospace editor
font/size with monospace/13px fallbacks. No Markdown rewrite, wrap disabling or
compact width increase is used. Browser probes verify that 80 ASCII M glyphs fit
the textarea's usable width and the actual revision pre remains one line without
horizontal overflow at 13, 14 and 16px. Native forms, layout and boundary routing
continue to measure intrinsic world bounds, not the viewport/camera. Arbitrarily
large/proportional/custom fonts and 80 wide Unicode glyphs are not guaranteed.

Git corners are 20px with 800 font weight instead of 14px/700, including R for
consistent presentation. Keep absolute bottom-right anchoring; reserve 26px of
badge-row space. Actual A/M/D browser checks verify size/weight, matching theme
colors, bounds and no collision with headlines, IDs or badges on unchanged
compact dimensions. Existing shorter-card content-fit assertions remain intact.

Two new shared regressions plus strengthened hover assertions check common
transient hover state, fixed expanded width, unchanged compact size and CSS
styling/marker/monospace contracts. Shared real-host tests now check white hovered
borders in root/other-node/expanded views, actual resting gray tint/theme text and
legend colors in all modes and dark/light/contrast probes, 80-column editor/pre
fit, and marker clearance. Existing routing/low-zoom strength/camera/headline,
watcher/draft and native-document assertions are not weakened or given more time.

Installed Windows Electron passed the complete host suite and recorded screenshots.
The first screenshot-enabled VS Code run passed the full canvas suite but timed
out during the separate native-document lifecycle/CDP checks. An unchanged isolated
rerun without screenshots passed the complete suite, including native save/undo,
raw-edit repair and independent split cameras. Timeout cause is not established;
retain the failed run rather than claiming every attempt succeeded. Inspected VS
Code root hover, wide Markdown/revision display and modified-letter screenshots
show the subdued gray core, white hovered outline and enlarged Git cue. Logs and
images stay in ignored local state, not in canonical graph files.

Current local checks passed: 107 shared UI tests, 34 VS Code adapter tests, nine
Electron tests, 100 Python tests, Ruff lint/format and both working graph validators
with warnings as errors. The root has 87 nodes; the independent Gantt graph has 44.
Host evidence is bounded Windows/browser/CSS-probe coverage,
not every installed theme, other-platform runs, arbitrary font sizing, exhaustive
accessibility or large-graph performance certification. No hooks are installed;
unrelated local settings/artwork remain untouched. Separate specification-first
and implementation commits retain revisable choices and exact staged validation.

---
id: X8Rqyk8=
type: implementation
parents:
- 6QB9hRY=
- IAy2dGI=
sources:
- path: graph-ui-common/media/graph-model.js
  symbol: exact seven RAINBOW_COLORS, TYPE_COLORS and REVISION_COLORS
- path: tools/rainbow-playground/palette.js
  symbol: DEFAULTS and generated export
- path: tools/rainbow-playground/index.html
  symbol: adopted parameter and slider defaults
- path: tools/rainbow-playground/README.md
  symbol: current palette defaults
- path: graph-ui-common/test/rainbow.test.cjs
  symbol: literal colors/mappings, OKLCH and seven-entry cycle
- path: graph-ui-common/test/playground.test.cjs
  symbol: exact user CSS/JSON and reset regressions
- path: graph-ui-common/test-host/playground.cjs
  symbol: seven-swatch real file browser defaults and exports
- path: graph-ui-common/test-host/ui.cjs
  symbol: shared real-host color/hover/label checks
- path: docs/own-spec.md
  symbol: user-selected seven-color table
---
## Later Added/Requirement mapping correction

B87C_kI= swaps the two role indices without changing the seven hex values or
parameters. The original mapping/export regression and actual check counts below
remain historical evidence. Current production and playground put Requirement at
color 5 and Added at color 4, with Added prioritized near the default green text
cue and Requirement using an available leftover. The later implementation record
will document current tests; this does not retroactively change earlier results.

# Apply the user's exact seven-color playground output

Implement gfAxHps= through revised 6QB9hRY= in the single shared graph model.
RAINBOW_COLORS is exactly #bc82c9, #7e97e6, #1facce, #37b390, #92a64b,
#ca8d3e, #dc7b7c, in that order. Zero-based mappings are requirement 3,
implementation 0, added 4, changed 1, removed 6, renamed 1 and source-changed 5.
Translate the user's one-based CSS variable references into the existing model
indices rather than installing inert CSS or a second conflicting palette source.

Distances already wrap by table length, so one hop is the first swatch, seven
the last and eight restarts. Preserve all four fill modes, gray/white-hover root
in distance/type modes, status-colored root in revision mode, neutral unknown/
unchanged/draft states, existing title/corner and edge cues and the independent
six-color label preview. No camera/form/geometry, persistence, CLI or node schema
change is needed; maintained example histories do not need rewriting.

The user subsequently provided full JSON, confirming count 7, L=.69, C=.12, hue
320 to 20 and no gamut reductions. Set the standalone playground's reset/default
controls to those parameters. Actual generation reproduces every supplied hex
and mapping; it does not reinterpret or adjust the user's selection. Update both
numeric/slider HTML defaults and palette.DEFAULTS, guide and export/browser checks.

Regression assertions compare the exact production color array and literal role
hex values, seven-entry cycle and independently converted OKLCH targets. The
playground default regression compares the complete supplied parameters, colors,
zero-based mappings and empty gamut-reduction list and checks CSS export against
the user's exact pasted :root block. Updated DOM/browser checks verify seven
swatches/eight node samples, reset and the final CSS color. Existing form/draft/
caret, native menus, label cycle, root/history/status and hover invariants remain.

Actual local Windows checks passed: 127 shared UI, 34 VS Code adapter, nine Electron
and 111 Python tests, Ruff lint/format and both working graph validators with
warnings as errors. The standalone file:// browser suite passed, including defaults,
controls, gamut feedback, JSON/CSS export/reset/light preview/copy fallback.
Full Electron and VS Code suites passed sequentially after build/compile via their
direct Node host runners, on independent maintained-history clones (44 target /
45 displayed nodes). All existing geometry/low-zoom/native text/forms/navigation,
label zero-state/geometry changes, watcher repair, VS Code native document lifecycle
and Electron save/sandbox/reload/history checks remain passing. Electron revision
palette and playground-default screenshots were inspected. No timeout/assertion
or production camera change was needed for these runs. Logs/screenshots remain
ignored local evidence; broader platform/display/accessibility claims are not made.

Refresh specification, README, technical conclusion, canvas guide and own-spec
context; retain older nine/thirteen-color choices and actual run counts explicitly
as history. Both host assets were rebuilt from the shared source. Tests used the
current worktree, which also contains unrelated pre-existing fixture/history/
workspace-policy changes; those changes are not part of this palette slice.
Stage only the intended graph/code/docs, validate that exact index and commit
separately from the specification change. Install or replace no Git hooks.

---
id: Flf59Uc=
type: implementation
parents:
- 6QB9hRY=
sources:
- path: graph-ui-common/media/graph-model.js
  symbol: RAINBOW_COLORS, TYPE_COLORS, REVISION_COLORS, REVISION_LABELS, COLOR_MODES, color
- path: graph-ui-common/media/graph.js
  symbol: revisionKind, drawLegend, compactCard, draw and mode restoration
- path: graph-ui-common/media/graph.css
  symbol: revision-colored exclusion from neutral manifesto white hover
- path: graph-ui-common/view.cjs
  symbol: Git/Revision Status option
- path: graph-ui-common/test/rainbow.test.cjs
  symbol: independent OKLCH palette and color mappings
- path: graph-ui-common/test/graph.test.cjs
  symbol: revision color, native drafts, no-comparison and orphaned/new draft regressions
- path: graph-ui-common/test-host/platform.cjs
  symbol: real modified manifesto fixture
- path: graph-ui-common/test-host/ui.cjs
  symbol: palette/revision fill and colored-root hover probes
- path: docs/own-spec.md
  symbol: shared rainbow and Git/Revision Status tour
---
## Later nine-color tuning

l3vgxN4= supersedes the thirteen swatches/counts below, not the revision-mode
behavior or earlier actual evidence. 6QB9hRY= now chooses nine slightly stronger
colors and remaps shared-table indices; the separate tuning record documents
current code and checks.

# Render a shared rainbow spectrum and comparison-status fills

Implement Rg30CXs= through the revisable choice 6QB9hRY= in the common renderer,
not host-specific palettes or canonical metadata. Replace the seven arbitrarily
ordered depth colors with thirteen in-gamut, rounded sRGB entries sampled at
OKLCH lightness .73/chroma .11, hues 300..30 every 22.5 degrees. One hop starts
violet; thirteen is red, fourteen restarts violet. Type teal/violet and colored
revision mappings reference the same RAINBOW_COLORS entries. Unknown distance and
neutral states use NEUTRAL_COLOR; non-positive/invalid non-root paths are neutral.

Add COLOR_MODES, REVISION_COLORS and REVISION_LABELS to the pure graph model. The
new color argument uses the selected comparison kind, independent of node type;
only other modes retain the gray manifesto exception. Existing renderer changes()
precedes source impact with direct diff kinds. Compact and expanded cards receive
A green, M/R blue, D red, source-only amber and unchanged neutral, including root
changes. No comparison is labeled explicitly and neutral; new/orphaned unsaved
drafts are neutral, not invented Git changes. Withdrawal labels never create D.

Expose Git/Revision Status via the shared template, restore/save git-revision in
host state and add a complete informative legend. Keep obsolete approval-status
preferences falling back to distance. Revision-colored cards carry a transient
presentation class; the neutral-root white-hover override excludes them, so a
status-colored manifesto retains its brighter/higher-chroma hue in compact and
expanded views. Other modes retain gray/white-hover root behavior. Existing edge
inks/dashes, title/corner theme tokens, min/max metrics and node records stay
independent. Switching modes moves the same native forms and preserves drafts,
caret, original contents, camera and geometry. No new mutating message is emitted.

Seven new unit regressions independently convert the hex table back to OKLCH to
check close ordered hues, stable lightness/chroma, uniqueness, cycle boundaries,
shared-table type/status mappings and gray versus status-colored manifesto.
Renderer regressions cover all comparison kinds, direct-change/source precedence,
compact/expanded/root/history/mode-switch behavior, withdrawal/source-only labels,
no comparison, persisted drafts/caret/camera/original records and neutral new or
orphaned drafts. Older all-mode fixed-gray tests are explicitly scoped to distance/
type; earlier approval-status fallback checks remain. There are now 115 common,
34 VS Code adapter and nine Electron unit tests; all passed, with 111 Python tests,
Ruff lint/format and both working graphs validated with warnings as errors.

Both complete real Windows host suites passed sequentially, with screenshots,
on independent maintained Gantt-history clones (44 target / 45 displayed nodes).
The shared platform harness uses the CLI to modify the disposable root and waits
for actual watcher/diff display before testing revision mode. Browser probes check
computed fill/legend/status mapping and same-hue lightness/chroma hover under dark,
light and both high-contrast CSS classes, expanded root hover, all palette colors,
unchanged geometry/camera and host-state persistence. Existing low-zoom/head joins,
painted clearance, native forms/navigation, themed Git cues, watcher invalid-file
repair, VS Code native save/undo/redo/split/CRLF/Unicode lifecycle and Electron
sandbox/save/reload/historical-comparison tests also passed without weakened
assertions or timeouts. Electron's malformed-file log errors are deliberate
recovery probes, not failures. Inspected distance/revision/expanded-root screenshots
show the softly colored palette, distinct revision fills and colored root hover.
Ignored local screenshots/logs are bounded evidence, not canonical graph artifacts.

Update README, own-spec tour, technical conclusion and canvas guide. Both host
assets were rebuilt from the common source. No schema change or example-history
rewrite was needed. Keep unrelated existing fixture/history/workspace-policy
changes unstaged; test runs exercised the current worktree, not a claim those
separate changes belong to this implementation. Use exact staged graph validation
before the authorized implementation commit; no hook installation/replacement.

Limits: current Chromium hosts and bounded CSS probes, not universal accessibility,
all OS/theme/browser/device/gamut or large-graph certification. More colors narrow
hue separation intentionally; palette constants remain revisable. sRGB rounding
is checked numerically; hover gamut mapping can limit extreme displayed chroma.
No approval workflow, new canonical status field, Git writer or host fork returns.

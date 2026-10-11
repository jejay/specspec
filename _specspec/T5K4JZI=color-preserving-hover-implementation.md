---
id: T5K4JZI=
type: implementation
parents:
- bLBNk80=
sources:
- path: graph-ui-common/media/graph.css
  symbol: edge-hover-ink and manifesto-only white hover border
- path: graph-ui-common/test/graph.test.cjs
  symbol: semantic border scope and colored incident ink regressions
- path: graph-ui-common/test-host/ui.cjs
  symbol: checkHover, checkHoverPalette, assertStrongerHue
- path: README.md
  symbol: hover colors
- path: docs/own-spec.md
  symbol: color-preserving hover correction
- path: docs/node-canvas.md
  symbol: connection hover
---
# Render stronger semantic hover colors with a manifesto-only white border

Implement pqNhV6s= through bLBNk80= in graph-ui-common/media/graph.css, the single
renderer source copied into both host builds. No schema or canonical metadata
change, new edge category or host fork is introduced. No example-history rewrite
is needed because this changes presentation, not the node schema.

Replace the all-card white border introduced by c2d8e15 with a relative OKLCH
non-root border: L + 0.10 capped at 0.95, C * 1.30, unchanged H, from node-accent.
A following manifesto-only override preserves the requested white border. Both
native :hover and transient node-hovered selectors share these rules, including
expanded and Git-overlay nodes. Existing shared fills, semantic accent values,
contrast-theme resting borders, width/styles, focus and darkening stay unchanged.

Added/removed/draft curve/head classes derive edge-hover-ink from their existing
edge-ink using the same lightness/chroma adjustment. Incident pairs use that ink
at full opacity; neutral normal links retain the theme-foreground mix as fallback.
Modified node state does not create a modified-edge color. Non-incident black
mixing, arrow/dash geometry, ordering and delegated pointer lifecycle stay intact.
No new filter/compositor hint or JS paint/mutation path is needed.

Regression checks now reject a global white override, require white only for the
manifesto, and require colored curve/head lightness/chroma derivation. Real-host
checkHover converts actual computed paint to OKLCH and asserts brighter lightness,
stronger chroma and retained hue, paired fill/stroke, full opacity and exact card/
edge restoration. It checks actual added/changed/removed hovered fixture nodes.
Real browser CSS probes cover all depth/type accents plus strong yellow, every
node Git state, compact/expanded cards, and added/removed/draft curve/head pairs
under dark/light/high-contrast/high-contrast-light themes. Existing membership,
SVG identity/order, path/head/width/dash geometry, camera, forms/caret/drafts,
low-zoom, routing, watcher and native-document checks remain, without loosening
timeouts or assertions. The old all-card-white tests encoded the misunderstanding,
not proof of what the user wanted.

Actual local Windows checks passed: 108 shared UI tests, 34 VS Code adapter tests,
nine Electron tests, 111 Python tests, Ruff lint/format, and root validation with
warnings as errors. Both complete installed-host suites passed sequentially on
independent maintained Gantt-history clones (44 target / 45 displayed nodes).
VS Code additionally passed native save/undo/redo, split synchronization/cameras,
raw invalid-buffer repair, CRLF/Unicode saves and independent node-file tabs.
Electron additionally passed sandbox/network, real saves, retained-draft reload,
watcher recovery and stage/02-code -> stage/03-spec comparison. The malformed-file
errors in the Electron log are intentional recovery probes, not suite failures.
VS Code added/changed/removed/root hover screenshots were captured and inspected;
logs/screenshots remain ignored local evidence. Both host assets were rebuilt.

Correct README, own-spec tour and canvas/conclusion docs together with the graph.
Keep unrelated pre-existing fixture/history/workspace-policy changes unstaged;
these tests ran against the current working tree, not a claim that those separate
changes were part of this implementation. Stage only this slice, validate the
exact staged graph and commit it separately from the intention/choice correction.
No hooks were installed or replaced, and local settings/artwork remain untouched.

Limits: relative OKLCH is verified in these installed Chromium hosts, not older
browsers or every OS/theme. Computed chroma can be gamut-mapped at paint time;
extreme custom colors/displays are not universally certified. Lightness/chroma
constants are revisable. Passing tests and commits are evidence, not approval.

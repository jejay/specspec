---
id: T5K4JZI=
type: implementation
parents:
- bLBNk80=
sources:
- path: graph-ui-common/media/graph.css
- path: graph-ui-common/test/graph.test.cjs
- path: graph-ui-common/test-host/ui.cjs
- path: README.md
- path: docs/own-spec.md
- path: docs/node-canvas.md
---
# Derive stronger same-hue card and incident-edge hover paint

Shared CSS derives colored hovered borders and added/removed/draft incident ink
with OKLCH L+0.10 capped .95, C×1.30 and unchanged H. Neutral distance/type manifesto
borders are white; revision-colored roots use their hue. Neutral normal links use
theme contrast; unrelated darkening retains its separate membership and ink.

Computed-paint tests convert actual browser colors to OKLCH and check brighter,
more saturated same-hue results, exact pair membership/restoration and stable
width/dashes/routes/head geometry/native forms. Evidence covers tested host/theme
probes with browser gamut and display conditions.

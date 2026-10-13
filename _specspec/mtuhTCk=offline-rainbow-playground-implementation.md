---
id: mtuhTCk=
type: implementation
parents:
- IAy2dGI=
sources:
- path: tools/rainbow-playground/index.html
- path: tools/rainbow-playground/palette.js
- path: tools/rainbow-playground/app.js
- path: tools/rainbow-playground/README.md
- path: graph-ui-common/test/playground.test.cjs
- path: graph-ui-common/test-host/playground.cjs
---
# Generate and export offline palettes with Added-first mapping

Local plain HTML/CSS/JS opens directly from disk. `palette.js` converts OKLCH to
linear/gamma sRGB, reports fixed-hue/lightness chroma reductions and chooses Added
nearest 149.5°, then Requirement's unused entry nearest 165° with ordered ties/reuse.
Defaults reproduce the exact seven colors and final role assignments.

`app.js` retains the last valid preview, handles numeric/slider controls, dark/light
samples, reset, JSON/CSS exports and clipboard/manual-copy fallback. A 150px gray
circle previews the manifesto. Labeling and copy output explain their experimental
purpose. Tests cover count/hue ranges, gamut, defaults, mapping priority/reuse,
invalid inputs, export/reset/copy and an installed-browser direct-file check.

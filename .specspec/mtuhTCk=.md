---
id: mtuhTCk=
type: implementation
parents:
- IAy2dGI=
sources:
- path: tools/rainbow-playground/index.html
- path: tools/rainbow-playground/palette.js
- path: tools/rainbow-playground/app.js
- path: graph-ui-common/test/playground.test.cjs
- path: graph-ui-common/test-host/playground.cjs
---
# Generate palettes offline, export them and map Added first

The playground in `tools/rainbow-playground` is plain HTML, CSS and JavaScript and opens directly from the disk. `palette.js` converts OKLCH to linear and to gamma-encoded sRGB and reports where it reduced the chroma at fixed hue and lightness. It assigns Added to the entry nearest to hue 149.5° and then Requirement to the unused entry nearest to 165°, with a tie going to the earlier entry and with reuse of an entry when all are used. Implementation takes the entry nearest to 300°, Modified nearest to 264°, Deleted nearest to 30° and source impact nearest to 75°. The defaults reproduce the seven exact colors and the role assignments of the product.

`app.js` keeps the last valid preview and handles the number fields and sliders, the dark and light samples, the reset, the exports as JSON and CSS, and the copy through the clipboard with the fallback of selecting the text for copying by hand. A gray circle of 150px previews the manifesto. The page labels itself as an experiment, and its message after a copy says to bring the result back to the assistant. `graph-ui-common/test/playground.test.cjs` and `graph-ui-common/test-host/playground.cjs` cover the ranges of count and hue, the gamut, the defaults, the priority and the reuse in the mapping, invalid input, export, reset and copy, and they open the page as a file in an installed browser.

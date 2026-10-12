---
id: mtuhTCk=
type: implementation
parents:
- IAy2dGI=
sources:
- path: tools/rainbow-playground/index.html
  symbol: offline controls, previews and export area
- path: tools/rainbow-playground/palette.js
  symbol: generate, sample, linearRGB, css
- path: tools/rainbow-playground/app.js
  symbol: render, exportResult and clipboard/manual copy
- path: tools/rainbow-playground/README.md
  symbol: direct opening and copy workflow
- path: graph-ui-common/test/playground.test.cjs
  symbol: seven generator and DOM regressions
- path: graph-ui-common/test-host/playground.cjs
  symbol: real file browser checks
---
## Later user-selected defaults

gfAxHps= supplies the exact seven-color CSS and JSON selection. X8Rqyk8= updates
current tool defaults to count 7, L=.69, C=.12, hue 320 to 20 and verifies exact
exports. The initial nine-color-default description and actual checks below are
historical; the standalone editing/export/gamut/copy behavior remains in scope.

# Build a separate offline rainbow parameter playground

Implement XLyy460= through IAy2dGI= in tools/rainbow-playground. Plain local
HTML/CSS/scripts open from file:// without a server, dependencies or graph access.
Default parameters reproduce the current nine production hex swatches exactly.
Count, lightness, chroma and hue endpoints update swatches, tinted/hovered node
samples, dark/light canvases and nearest-hue type/Git suggestions. Reset restores
default parameters. Invalid input retains the last valid preview/export and
disables automatic copy. No filesystem, browser-storage or production palette
mutation/import path exists.

palette.js converts OKLCH through linear sRGB/gamma encoding, reducing chroma by
binary search for out-of-gamut samples at fixed lightness/hue. Report reduced
indices; full result lists rounded hex colors and suggested zero-based mappings.
Export either parameters-only JSON, full palette JSON or valid CSS custom-property
snippets. This is a standalone export format, not a new canonical node API/schema.
Clipboard API success is reported only after it resolves; rejection/unavailability
selects the textarea and explains manual Ctrl+C/Cmd+C. Project text is not evaluated
or imported, and exports are not executable palette-installation instructions.

Seven focused generator/DOM regressions passed within the current 127-test common
worktree suite: exact production defaults/mappings, both interpolation directions,
parameter limits, fixed-lightness/hue gamut reduction and black/white extremes,
number/slider inputs, export formats/theme/reset, invalid edits and copy/fallback.
An initial copy test flushed only one microtask across JSDOM realms; it was fixed
to wait for event-handler completion without changing production copy semantics.
The separate real Chromium/Electron file:// harness passed startup, computed tinted
paint, count/chroma editing, gamut feedback, full JSON/CSS export, invalid input,
reset, light preview and manual-copy fallback. It never writes the user's clipboard.
Captured screenshots were inspected; ignored local logs/images are bounded evidence.

The harness is optional developer verification using existing Electron/Node 22+,
not a runtime dependency of the standalone page. README and own-spec guide provide
direct opening/copy instructions. Current other checks passed: 34 VS Code adapter,
nine Electron and 111 Python tests, Ruff and graph validation. These ran in a
worktree also containing the independent label slice and unrelated pre-existing
changes; the separate label implementation record describes its host evidence.
Stage only this tool/docs/spec slice and validate the exact index before its
separate commit. Install/replace no hooks. Constants/gamut/perception limits and
hue-based mapping suggestions remain revisable, not accessibility certification.

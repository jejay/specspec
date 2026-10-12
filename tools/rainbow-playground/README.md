# Rainbow playground

Open [`index.html`](index.html) directly in a recent browser (double-click it).
No server, installation, network connection or SpecSpec project is needed.
Keep `index.html`, `palette.js` and `app.js` together.

Adjust:
- **Number of colors**: 2–32.
- **Lightness**: OKLCH L, 0–1.
- **Chroma**: a saturation-like control, 0–0.4.
- **Start/end hue**: degrees, interpolated linearly in the given direction.

Defaults reproduce the user's adopted seven-color palette: L=.69, C=.12, hue 320 → 20.
View plain swatches and hoverable tinted nodes on dark/light canvases. The suggested
Git choices are nearest-hue table entries: Added targets the default green text
cue (#81b88b, OKLCH hue ≈149.5°) before assigning Requirement. Other role hue
targets are unchanged. Requirement receives an unused swatch nearest hue 165°
after the other roles; if none remains, it reuses the nearest swatch. At the
defaults, Added is color 4 (#37b390) and Requirement color 5 (#92a64b).
Small/narrow palettes may map several meanings to the same color. The fixed
reference is not live host-theme matching. These suggestions do not change SpecSpec.

Choose **Parameters JSON** (enough), **Full palette JSON**, or **CSS variables**,
then **Copy result** and paste it back to the assistant. If clipboard access is
blocked, the text is selected for Ctrl+C / Cmd+C. The CSS is a standalone snippet,
not an automatic import. Nothing is saved to files, browser storage or the CLI.

Out-of-sRGB-gamut samples reduce chroma while retaining requested lightness/hue;
the preview reports which samples changed and full JSON lists their indices.
Base hex rounding, browser hover gamut mapping and display differences can affect
appearance. This is an experiment, not an accessibility/contrast guarantee.

## Development checks

Pure-generator and DOM tests run with `npm --prefix graph-ui-common test`.
Optional real file:// browser check using the existing Electron dev installation:

```sh
node graph-ui-common/test-host/playground.cjs
```

That harness needs Node 22+ and `electron/node_modules`; the playground itself has
no dependency on them. `SPECSPEC_SCREENSHOT_DIR` optionally captures its preview.

# SpecSpec identity

The application uses the owner's selected **W / Spectrum flow + Q / Shorter runs
+ M / Mirrored Prism** identity from `../specspec-branding/final/` (Identity 1.0).
The sibling workspace is the design source; builds use only this repository's
local copies and need no sibling checkout or network access.

- [`activity-icon.svg`](activity-icon.svg) is a byte-identical copy of
  `final/icons/specspec-icon-24.svg`: the optical 24×24 circle → S → square symbol.
  The shared 24px header uses its alpha mask, colored by the host foreground.
  This single-ink treatment follows native theme and contrast
  conventions. The symbol has the accessible name “SpecSpec”; the header shows
  only the symbol followed by the live revision label.
- [`app-icon.png`](app-icon.png) is a byte-identical copy of
  `final/png/specspec-app-icon-512.png`, the supplied spectrum launcher tile for
  Electron windows and extension packaging. The small icon is its own optical
  drawing, not a scaled launcher or detailed mark.
- [`specspec-logo-light.svg`](specspec-logo-light.svg) and
  [`specspec-logo-dark.svg`](specspec-logo-dark.svg) import the primary full logos
  byte-for-byte; matching transparent PNGs support README/package introductions.
  Keep the supplied geometry and continuous gradient. The wordmark needs no font.
- [`app-icon.ico`](app-icon.ico) is a Windows launcher container generated from the
  unchanged supplied PNG, not another logo design. `python tools/build_icon.py`
  regenerates its native sizes using the developer-only Pillow dependency.
- [`identity.sha256.json`](identity.sha256.json) records original source paths and
  SHA-256 digests for the byte-identical imports. The optical SVG is a non-text Git asset to
  preserve its exact bytes on every checkout. Artifact tests verify the local copies.

The selected source geometry remains intact. Brand colors identify the product;
existing graph, Git, influence and diagnostic palettes retain their own semantics.
No font is needed for these vector/raster assets. The header omits the wordmark
and optional tagline.

## Preserved owner inputs

The supplied [`Monochrome_Dachshund_Puppy_Emblem.svg`](../Monochrome_Dachshund_Puppy_Emblem.svg)
and [PNG](../Monochrome_Dachshund_Puppy_Emblem.png) remain preserved at their original
paths. [`dachshund.svg`](dachshund.svg) is still a byte-identical archival import,
protected alongside the original SVG by non-text Git attributes. These owner
inputs are retained as artifacts; application builds use the identity above.

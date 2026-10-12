---
id: Aq02oUE=
type: implementation
parents:
- ALlkmT0=
sources:
- path: branding/README.md
  symbol: derivation, resvg commands and original preservation
- path: branding/activity-icon.svg
  symbol: 24x24 minimal puppy-face mask
- path: branding/app-icon.png
  symbol: resvg 256px original-brand render
- path: branding/dachshund.svg
  symbol: byte-preserving supplied artwork
- path: Monochrome_Dachshund_Puppy_Emblem.svg
  symbol: versioned original supplied SVG
- path: Monochrome_Dachshund_Puppy_Emblem.png
  symbol: versioned original supplied PNG
- path: .gitattributes
  symbol: exact original/import SVG checkout bytes
- path: tests/test_repository_docs.py
  symbol: exact artwork import and PNG signature
---
# Import the brand and render a minimal themed dog icon

branding/dachshund.svg preserves the supplied SVG byte-for-byte. The distinct
24x24 activity-icon.svg simplifies floppy ears, head/muzzle, eyes and nose using
1.5-unit monochrome strokes and negative space, without a black backing, bitmap,
script or external reference. resvg rendered 24px light/dark and 240px previews;
all were inspected. resvg also produced the versioned 256px app-icon.png from the
full original artwork for native/extension package icons. The Activity Bar and
shared header use a theme/current-color mask; real Windows screenshots were
inspected. At that checkpoint originals remained untouched and untracked. This is scoped visual evidence,
not universal legibility/raster quality or a claim of unrelated artwork ownership.
No Electron/third-party icon is substituted for the user's dachshund brand.

## Original-input completion

1aSOZOs= now versions the original loose SVG/PNG unchanged at their original
paths. The branding SVG remains byte-identical to the original; Git attributes
disable SVG text conversion. The new repository artifact regressions check exact
import bytes and PNG signature. Existing derivative/icons and the earlier resvg/
real-host legibility evidence are unchanged, not new renders or raster guarantees.

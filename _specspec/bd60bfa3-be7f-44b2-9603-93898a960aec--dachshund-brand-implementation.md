---
id: bd60bfa3-be7f-44b2-9603-93898a960aec
type: implementation
parents:
- a1595f98-cae9-4593-aae9-baff7789b435
sources:
- path: branding/dachshund.svg
  symbol: byte-preserving supplied artwork
- path: branding/activity-icon.svg
  symbol: 24x24 minimal puppy-face mask
- path: branding/app-icon.png
  symbol: resvg 256px original-brand render
- path: branding/README.md
  symbol: derivation, resvg commands and original preservation
---
# Import the brand and render a minimal themed dog icon

branding/dachshund.svg preserves the supplied SVG byte-for-byte. The distinct
24x24 activity-icon.svg simplifies floppy ears, head/muzzle, eyes and nose using
1.5-unit monochrome strokes and negative space, without a black backing, bitmap,
script or external reference. resvg rendered 24px light/dark and 240px previews;
all were inspected. resvg also produced the versioned 256px app-icon.png from the
full original artwork for native/extension package icons. The Activity Bar and
shared header use a theme/current-color mask; real Windows screenshots were
inspected. Originals remain untouched/untracked. This is scoped visual evidence,
not universal legibility/raster quality or a claim of unrelated artwork ownership.
No Electron/third-party icon is substituted for the user's dachshund brand.

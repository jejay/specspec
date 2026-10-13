---
id: Aq02oUE=
type: implementation
parents:
- ALlkmT0=
sources:
- path: branding/README.md
- path: branding/activity-icon.svg
- path: branding/app-icon.png
- path: branding/dachshund.svg
- path: Monochrome_Dachshund_Puppy_Emblem.svg
- path: Monochrome_Dachshund_Puppy_Emblem.png
- path: .gitattributes
- path: tests/test_repository_docs.py
---
# Supply original and derivative dachshund assets

The versioned supplied PNG/SVG retain their input bytes. `branding/dachshund.svg`
is an exact SVG copy, protected by non-text Git attributes. `activity-icon.svg`
is a distinct 24×24 monochrome face contour mask. `app-icon.png` is a 256px render
of the full supplied artwork. Host/package chrome shares these assets.

Artifact tests check exact SVG import, PNG signature, attributes and local guide
links. Offline render commands in the branding guide support miniature contrasting
inspection, scoped to the actual raster/display conditions.

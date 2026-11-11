---
id: Aq02oUE=
type: implementation
parents:
- ALlkmT0=
sources:
- path: branding/activity-icon.svg
- path: branding/app-icon.png
- path: branding/identity.sha256.json
- path: branding/dachshund.svg
- path: Monochrome_Dachshund_Puppy_Emblem.svg
- path: Monochrome_Dachshund_Puppy_Emblem.png
- path: .gitattributes
- path: tests/test_repository_docs.py
- path: vscode/scripts/build-webview.cjs
- path: electron/scripts/build.cjs
---
# Package the selected identity and preserve original owner artwork

`branding/activity-icon.svg` is an exact import of `final/icons/specspec-icon-24.svg`, and `branding/app-icon.png` is an exact import of `final/png/specspec-app-icon-512.png`. The local manifest `branding/identity.sha256.json` records the source paths and the digests of the imported bytes. The builds in `vscode/scripts/build-webview.cjs` and `electron/scripts/build.cjs` copy these assets into the offline output of each editor. The shared header fills the optical symbol, used as a mask, with the foreground color of the editor, and the launcher shows the supplied spectrum tile.

The dachshund artwork that the owner supplied is preserved: `Monochrome_Dachshund_Puppy_Emblem.png` and `Monochrome_Dachshund_Puppy_Emblem.svg` at the root of the repository, and `branding/dachshund.svg` as an archival import with the same bytes as the supplied SVG. `.gitattributes` marks the SVG files as non-text, so that Git leaves their bytes alone. The artifact tests in `tests/test_repository_docs.py` check the preserved archive, the digests of the current imports, the geometry of the optical icon, the dimensions of the launcher and the copies in the built editors.

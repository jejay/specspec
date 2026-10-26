---
id: Aq02oUE=
type: implementation
parents:
- ALlkmT0=
sources:
- path: branding/README.md
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

branding/activity-icon.svg imports final/icons/specspec-icon-24.svg exactly, and
branding/app-icon.png imports final/png/specspec-app-icon-512.png. The local digest
manifest records source paths and exact import bytes. Host builds copy these
assets to their own offline outputs. The shared header applies the optical
symbol as a host-foreground mask; the launcher retains its supplied spectrum tile.

The loose supplied dachshund PNG/SVG and byte-identical SVG archival import remain
preserved with non-text attributes. Artifact tests check archival preservation,
current import digests, optical geometry, launcher dimensions and built host copies.

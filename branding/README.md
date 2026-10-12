# SpecSpec dachshund

`dachshund.svg` is an exact, byte-preserving import of the project owner's provided
[`Monochrome_Dachshund_Puppy_Emblem.svg`](../Monochrome_Dachshund_Puppy_Emblem.svg).
That original SVG and the supplied [PNG](../Monochrome_Dachshund_Puppy_Emblem.png)
are versioned unchanged at their original paths. Git attributes disable line-ending
conversion for both the original SVG and its byte-identical branding import.
The full white puppy emblem on black is the brand artwork. `app-icon.png` is its
256-pixel `resvg` rendering for Electron/extension package icons.

`activity-icon.svg` is a separate minimal 24×24 monochrome face: long floppy ears,
head/muzzle, eyes and nose. It uses 1.5-unit strokes, rounded joins and negative space,
no black background, embedded bitmap, text, external reference, or script. VS Code
uses its alpha mask and applies the current Activity Bar foreground. The shared
header also uses a current-color CSS mask. The original detailed puppy is not squeezed
into the tiny mask.

The command-line `resvg` tool rendered 24px light/dark and 240px enlarged previews,
which were visually inspected, as were the real Activity Bar and Electron header.
These are platform-specific legibility checks, not universal raster guarantees.

```sh
resvg -w 256 branding/dachshund.svg branding/app-icon.png
resvg --background '#ffffff' -w 24 branding/activity-icon.svg /tmp/icon-light.png
# For a dark preview, supply a stylesheet with: svg { color: #cccccc; }
resvg --stylesheet /tmp/icon-dark.css --background '#1f1f1f' -w 24 \
  branding/activity-icon.svg /tmp/icon-dark.png
```

The SVG is provided project artwork; the simplified derivative is project code/art
under the repository license. No third-party icon/font or Electron trademark is used
as the SpecSpec brand. Raster previews are ignored diagnostics, not canonical graph
metadata. VS Code assigns new containers after built-ins; drag the dachshund below
Run and Debug if desired rather than relying on unsupported manifest ordering.

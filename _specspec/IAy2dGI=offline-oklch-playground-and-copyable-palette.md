---
id: IAy2dGI=
type: requirement
parents:
- XLyy460=
- 6QB9hRY=
---
# Generate copyable OKLCH palettes in an offline playground

Use local plain HTML/JS/CSS in `tools/rainbow-playground`, opening directly from disk.
Defaults are count 7, L=.69, C=.12, hue 320→20. Expose count 2–32, lightness/chroma
and hue endpoints, dark/light preview, reset, swatches and tinted/hover samples.
Interpolate linearly between hue endpoints in either direction. A 150px gray circle
illustrates the manifesto; other distance samples are generic tinted cards.

Convert OKLCH to sRGB. Out-of-gamut samples reduce chroma by binary search at fixed
lightness/hue and report their indices. Exports include parameters JSON, full palette/
mapping JSON and CSS custom properties. Clipboard success follows resolved writes;
unavailable/rejected clipboard selects text for manual copy. Invalid inputs retain
the last valid preview and disable automatic copy. Exports are deliberately applied
by the owner/assistant through an authorized change.

Prioritize Added at hue 149.5°, based on the fixed default added text `#81b88b`.
Retain other hue targets and changed/renamed reuse. Assign Requirement last to the
unused entry nearest hue 165°, or the nearest full-table entry when all are used.
Equal distances choose the earlier entry. Explain the fixed-reference priority and
reuse; host themes and actual display perception have their own conditions.

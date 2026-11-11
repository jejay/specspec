---
id: IAy2dGI=
type: requirement
parents:
- 6QB9hRY=
---
# Generate OKLCH palettes in an offline playground and offer them for copying

The playground is plain HTML, JavaScript and CSS in `tools/rainbow-playground` and opens directly from the disk. Its defaults are 7 colors, lightness 0.69, chroma 0.12 and a hue sweep from 320 to 20. It offers a count from 2 to 32, lightness, chroma and the two hue endpoints, a preview on a dark and on a light canvas, a reset, swatches and samples of tinted and hovered cards. The hue is interpolated linearly between the endpoints, in either direction. A gray circle of 150px shows the manifesto, and the other samples for distances are generic tinted cards.

A color is converted from OKLCH to sRGB. A sample outside the gamut gets its chroma reduced by a binary search at fixed lightness and hue, and the indices of such samples are reported. The exports are the parameters as JSON, the full palette with its mapping as JSON, and CSS custom properties. A copy counts as successful once the write to the clipboard has resolved, and when the clipboard is unavailable or refuses, the text is selected for copying by hand. Invalid input leaves the last valid preview in place and disables the automatic copy. The playground applies nothing to specspec by itself: the owner or the agent brings an export into the product through a deliberate, authorized change.

The mapping gives Added priority at hue 149.5°, the hue of the fixed default color of added text, `#81b88b`. The other roles have hue targets of their own: Implementation 300°, Modified 264°, Deleted 30° and source impact 75°. Requirement is assigned last, to the unused entry nearest to hue 165°, or to the nearest entry of the whole table when all are used. Of two entries at the same distance the earlier one is taken. The page explains the priority of the fixed reference and the reuse of entries. The theme of an editor can set other colors, and how a display shows them has conditions of its own.

---
id: IAy2dGI=
type: requirement
parents:
- XLyy460=
- 6QB9hRY=
---
# Offer an offline OKLCH playground with copyable results

Use tools/rainbow-playground/index.html plus local plain JS/CSS, no server, CDN,
packages, CLI, project access or production asset dependency. Open directly from
disk. Default to the current adopted seven-color parameters: count 7, L=.69, C=.12,
hue 320 to 20. The generator reproduces the seven swatches with the later Added/Requirement
swap from B87C_kI=.
Expose count, lightness, chroma and hue endpoints, a dark/light preview, reset,
color swatches and tinted/hovered node-style samples. Interpolate linearly from
start to end hue, not an implicit shortest-path rotation.

Export parameters JSON, a complete hex palette/mapping result and optional CSS
custom properties. Copy with Clipboard API when available, otherwise select text
for manual copy without claiming success. No automatic graph import/apply or
filesystem/browser-storage persistence. Parameters may be pasted to the assistant.

Convert OKLCH to sRGB numerically. If a requested sample is out of gamut, reduce
chroma at fixed lightness/hue and report that reduction; do not silently clip RGB.
Prioritize Added near the default Git added text cue (#81b88b, OKLCH hue about
149.5 degrees); keep other role hue targets. Give Requirement the nearest
to-green unused entry after those roles (target hue 165). If none is unused,
fall back to the nearest entry; narrow palettes may share meanings. Explain the
priority and fixed default-text reference in the preview, not live host-theme
matching. These are suggestions, not an approval or production mutation. Validate inputs and retain the last valid preview if invalid.
Verify default output matches current table, interpolation/gamut behavior, exports,
reset, invalid edits and actual standalone browser startup. Perception/display and
hover gamut limits remain revisable; this tool does not certify accessibility.

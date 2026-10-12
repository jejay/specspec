---
id: gfAxHps=
type: requirement
parents:
- Rg30CXs=
- XLyy460=
---
# Adopt the user's exact seven colors and role mappings

Implement the palette selected in the standalone playground, exactly in this order:
#bc82c9, #7e97e6, #1facce, #37b390, #92a64b, #ca8d3e, #dc7b7c.

Use color 4 for requirements, 1 for implementations, 5 for added nodes, 2 for
changed/renamed nodes, 7 for removed nodes and 6 for source-only impact. The
numbered references are one-based, as in the user's pasted CSS custom properties.
Distance spectra repeat this seven-entry table. This replaces the previous nine
swatches/count and role indices, not the manifesto exceptions, transient label
trial, existing title/edge cues or hover/navigation/editing behavior.

Origin: the user's explicit CSS palette and role-mapping result. Preserve the
chosen hex values; do not silently retune them into another generated palette.

The user also supplies the full playground JSON: count 7, lightness .69, chroma
.12, startHue 320, endHue 20; zero-based mappings requirement 3, implementation 0,
added 4, changed 1, removed 6, renamed 1, source-changed 5, and no gamut reductions.
Use these explicit parameters for playground defaults and exact export regression.

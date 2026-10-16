---
id: JVHv1gc=
type: requirement
parents:
- HlpFtiA=
- FHfnj08=
- pWgqwcQ=
---
# Normalize revision-local influence on a continuous warm ramp

Reuse each full revision's unique descendant counts and longest manifesto paths.
For count c and highest non-manifesto count M, Absolute influence uses c/M and
Log Absolute Influence uses log1p(c)/log1p(M). For cohort minimum lo and maximum hi
at the node's maximum manifesto distance, Relative influence uses (c-lo)/(hi-lo).
Log Relative Influence uses (log1p(c)-log1p(lo))/(log1p(hi)-log1p(lo)). Apply the
logarithm to each raw count before subtracting the transformed minimum. Any fixed
logarithm base gives the same normalized result; use natural log1p numerically.

A zero denominator maps to zero: equal-count groups, singleton groups and all-zero
graphs use green. The manifesto retains its neutral gray accent and white hover
border, outside the influence scales. Unknown or cycle-blocked path context and
unsaved new/orphaned drafts use neutral presentation.

Map the normalized value continuously through green #4df884 at zero, yellow
#e8d62c at one half and red #ba2208 at one. Piecewise-linear sRGB interpolation
between these warm Turbo-like anchors supplies the continuous ramp and its legend.
Existing distance/type/revision palettes retain their exact mappings.

Surviving nodes use target counts/cohorts and deleted nodes use their complete base
revision, independent of focused visibility, placement backbones and comparison
unions. Build raw count ranges lazily once per revision metrics instance and share
them across all four influence modes. Ordinary distance/type/revision views retain
their existing metric cost. Persist each mode separately as view state. Mode switches
preserve canonical records, native forms/caret/drafts, camera, positions, routing
and independent Git and spotlight cues. Legends show the manifesto swatch and
gradient endpoints. The tutorial explains domains, normalization and ties.

---
id: bLBNk80=
type: requirement
parents:
- pqNhV6s=
- -0ljwrM=
- xCOHepQ=
---
# Raise hover lightness and chroma without whitening semantic colors

Keep shared card tints, theme text and transient node-hovered state. Limit the
white border override to .manifesto. For other hovered cards derive the border
from --node-accent using relative OKLCH: increase lightness by 0.10 (ceiling 0.95),
scale chroma by 1.30 and retain hue. Border widths/styles and semantic accent
records stay unchanged, including comparison/withdrawal/source cues.

For added, removed and draft incident curve/head pairs derive ink with relative
OKLCH: increase lightness by 0.10 (ceiling 0.95), scale chroma by 1.30 and retain
hue, at full opacity. Do not mix these colored inks with white/theme foreground.
Normal neutral relationships retain the existing theme-foreground contrast mix;
modified nodes can have normal, added or removed relationships. No new modified
edge category is introduced. Browser gamut mapping limits extreme/custom colors;
these constants remain revisable, not universal accessibility guarantees.

Keep unrelated darkening, SVG ordering, width/dash/path/head geometry, camera and
native form/draft/caret invariants. Verify actual computed lightness/chroma/hue,
not merely changed paint or unchanged classes, in dark/light/contrast probes,
all node Git states, yellow/non-root versus white/root borders, expanded cards,
historical/draft links, normal/minimum zoom and exact exit restoration.

Trace: 0d8d44b (2026-10-11) introduced the incorrect all-card white-border choice
in xCOHepQ=; c2d8e15 implemented it globally and tested it. Its parent iktVTRU=
requested white only for the gray root. 34e72bb (2026-10-06) introduced the 50%
edge-ink/theme-foreground mix behind the washed-out colored hover. Preserve this
history while superseding those choices; tests passing did not validate intent.

## Colored-root revision-mode extension

6QB9hRY= adds revision fills, including the manifesto. In that new mode a root
keeps stronger status-hue hover like other cards rather than becoming white. The
neutral-gray manifesto white-hover exception remains in distance/type modes.

---
id: xCOHepQ=
type: requirement
parents:
- iktVTRU=
- 6MUwTIw=
- LtROyww=
- fdB9ZLM=
---
# Reuse shared card tints, widen only expanded cards and strengthen Git corners

Keep the manifesto accent #d3d3d3, but remove its solid background, dark text and
special badge/contrast-theme rules. Share the 15% accent resting fill and 24%
hover fill for compact and expanded cards alike, with ordinary theme text. Use
one transient node-hovered class from existing delegated hover state. Only the
manifesto gets a white hover border; other hovered borders emphasize their own
semantic hue. Keep contrast-theme resting background/borders shared too. The
original all-card white-border choice in 0d8d44b overgeneralized the root request
and is superseded by bLBNk80=. Leave existing relationship emphasis,
non-neighbor darkening, palette metrics and truthful gray legends intact.

Increase fixed expanded world width from 620 to 860 units, leaving compact cards
264 by 112. Give textarea and revision pre text the same host editor monospace
font (fallback monospace) and editor font size (fallback 13px). Verify 80-column
ASCII at representative 13/14/16px fonts in the installed browser, both editor and
revision display, without wrapping or horizontal overflow. This is a typical-font
budget, not a guarantee for arbitrarily large/proportional font customizations or
80 wide Unicode glyphs. Retain soft wrapping for longer lines. Width remains
independent of viewport/camera, and the existing intrinsic layout/routing handles
this larger expanded card without a compact-card size increase.

Increase all Git corners, including rename R consistently, from 14px/700 to
20px/800. Keep them absolutely anchored in the existing bottom-right corner and
reserve 26px badge-row space rather than enlarging compact cards. Verify no
heading/metadata/badge collision or clipping, and maintain matching Git title/
letter colors and full state labels. These pixel/weight choices remain revisable.

Extend model/DOM/CSS and real-host tests for uniform hover/fill restoration,
expanded width, native editor/caret/geometry, actual 80-column fitting and enlarged
Git corners. Record the earlier solid-gray evidence as superseded history, not
proof the user requested that appearance. No host renderer fork, canonical UI
metadata, text reformatting, or permanent compositor hint is introduced.

Width tuning: use 860 rather than the initial 820-unit candidate to retain margin
for textarea padding and a vertical scrollbar at representative 16px monospace
fonts. Actual 80-column fit passes in both installed host browsers.

## Later type-shape revision

Dn6Ult8= changes roundness only, with AZbsoEA= choosing type radii
and a genuinely circular manifesto in compact/expanded views. The earlier all-card
compact dimensions and expanded outer width above remain the original sizing
choice; they now apply to ordinary Requirement/Implementation cards. The manifesto
uses a square outline fitted around its unchanged native editor content budget.
Colors, text, hover, Git cues and existing actual checks are not retroactively changed.

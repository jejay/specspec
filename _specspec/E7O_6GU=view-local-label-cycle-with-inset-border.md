---
id: E7O_6GU=
type: requirement
parents:
- DG-JpDc=
- bLBNk80=
---
# Paint editable highlight rings inside unchanged card outlines

One editable highlight set supplies a solid equal-inset outline around exact
matching members in the displayed graph, including base-revision removed cards.
Use 5 world units at actual size. At camera scale k, use
width = max(5, 3 / k) world units and set the outline offset to its negative,
following graph scale while preserving at least 3 CSS screen pixels at low zoom.
Each member uses its assigned color, from manual gestures or a spotlight. The
outline follows the existing type shape, retains its hue on hover and follows
unrelated-card darkening. Keyboard focus has an independent cue.

Keep editable highlights separate from canonical data, native forms, drafts and
semantic fills. Applying a spotlight replaces highlights and explicitly frames its
matching set; manual cycling and clearing only repaint. Arrivals and dropdown
opening/dismissal preserve camera, native input and caret. Node chrome and native
controls retain normal context menus. Compact counts explain changed-version,
absent and unavailable members without ringing them.

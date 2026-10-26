---
id: 6MUwTIw=
type: requirement
parents:
- pWgqwcQ=
- RlFT4io=
- -0ljwrM=
- qnGsij4=
- YOPhqYc=
---
# Darken only outside immediate displayed relationships

Use the hovered card plus endpoints of its incident drawn edges as the undarkened
set. Darken other cards with `brightness(.45)` and non-incident curve/head ink with
35% ink / 65% black. A link between two neighbors darkens unless it is incident.
An isolated hovered card leaves only itself undarkened. Include drawn history,
reverse and draft links; the neutral manifesto follows the same membership rule.

Reapply classes after redraw, including unchanged hovered identity; hit-test after
camera motion and restore on exit/blur/cancel/touch. Preserve shared tints, theme
text, semantic hues, forms/caret, edge geometry and pair ordering. Hover state is
transient renderer presentation.

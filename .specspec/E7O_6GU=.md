---
id: E7O_6GU=
type: requirement
parents:
- DG-JpDc=
---
# Paint every highlighted card with one ring of an adjustable ink inside its outline

The one editable set of highlights paints a solid ring, inset by the same amount on all sides, on every selected node that the displayed target or the deleted part of the base holds. The CSS variable `--spotlight-color` supplies the one ink, which is easy to change: white on dark themes and a dark ink on light themes, each with a contrast of at least 3:1 against the cards. The ink is independent of the fill colors and of the marks of Git changes. At camera scale `k` the ring is `max(5, 3 / k)` world units wide and is offset inward by the same amount, so that it shows at least 3 CSS pixels on the screen. The ring follows the shape of the card type and is darkened together with a card that the hover darkens. The cue for keyboard focus is separate from the ring, and the ring leaves the geometry of the card as it is.

Applying a spotlight closes the dropdown, switches the comparison and frames the members that are available. A toggle by hand and a clear repaint the rings and do nothing else. The arrival of a spotlight and the closing of the dropdown leave the camera, the drafts, the inputs of the form and the text cursor as they are. A visible warning about drift, which advises, and short notes on missing members and on the context accompany rings that are painted as well as the available nodes allow.

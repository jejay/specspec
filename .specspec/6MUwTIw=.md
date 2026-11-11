---
id: 6MUwTIw=
type: requirement
parents:
- RlFT4io=
- -0ljwrM=
---
# Darken every card and link outside the direct relationships of the hovered card

While a card is hovered, the hovered card and the endpoints of the links drawn to or from it stay undarkened. Every other card is darkened with `brightness(.45)`, and the curve and arrowhead of every link that does not touch the hovered card take an ink of 35% of their own color and 65% black. A link between two neighbors of the hovered card is darkened, because it does not touch the hovered card itself. A hovered card without links leaves only itself undarkened. The links of an earlier revision, links drawn against the direction of the layout and the links of a draft count like every other drawn link, and the gray manifesto is darkened by the same rule as every other card.

The classes are applied again after each redraw, also when the hovered card is the same as before. After a camera movement the card under the pointer is determined again, and the darkening ends when the pointer leaves, the window loses focus, the pointer is cancelled or a touch arrives. A hover changes paint alone: the tints, the text color of the theme, the hues of the fills, the form with its text cursor, the geometry of the links and the order of the pairs of curve and arrowhead are the same during and after it. The hover state exists in the renderer alone, for as long as the hover lasts.

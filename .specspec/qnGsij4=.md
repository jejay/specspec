---
id: qnGsij4=
type: requirement
parents:
- 7woeTpk=
- qf5-4sc=
- bOXyw00=
---
# Keep fill colors, Git marks and line patterns independent, and attach links to the measured outlines of the cards

The fill of a card shows the selected color meaning: it fits the theme, follows the zoom level and is explained by a short legend. Independently of the fill, the color of the headline and the letter in the corner show the Git status of a node, the line patterns show the status of a relationship, and a text cue shows that linked sources changed. The settings of the presentation are stored for each view. The record of a node carries the ID and the text of its node file in full, and the geometry of the graph and the values behind the colors are derived from the records.

Before the links are routed, the border box of every card is measured as the browser lays it out. The ports of a card are spread along its side and lie on the actual outline of its shape, and the links run as curves through the corridors reserved around the cards in their way. When the owner resizes an input of the expanded card, the geometry is computed again around the same form element. The pure functions for layout and metrics are bundled locally, and probes in the installed editors verify that the painted links keep clear of the cards.

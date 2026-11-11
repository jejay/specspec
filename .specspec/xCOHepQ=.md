---
id: xCOHepQ=
type: requirement
parents:
- iktVTRU=
- fdB9ZLM=
---
# Tint all card types alike, fit 80 columns into the expanded form and set bold Git letters in the corner

At actual size every card type has the same rule for its tint, 15% of the accent color at rest and 24% on hover, and the ordinary text color of the theme. Zoomed out, the fill follows the rule for the overview. In high-contrast themes all card types share one look at rest. On dark themes the manifesto of the distance and type modes has the accent `#d3d3d3` and a white border on hover, and on light themes its neutral border is darker, with a contrast of at least 3:1 against the card. Every other colored border, and the border of a manifesto colored by revision status, is emphasized in its own hue on hover.

An expanded card of a requirement or an implementation is 860 world units wide and gives the form 822px of width. The expanded circle of the manifesto holds the same 822px. The inline editor of the node text and the textarea of the sources use the monospace font and the font size that the theme of the surrounding editor sets, and `monospace` at 13px where it sets none. Longer lines wrap softly. A typical line of 80 ASCII columns fits at font sizes of 13, 14 and 16px, which tests verify.

The corner letter of a Git change is 20px high with weight 800 and is anchored absolutely in the bottom right corner of the card, and the row of badges keeps 26px clear beside it. Heading, badges and letter fit an ordinary compact card of 264×112, and the letter on a round manifesto fits inside its arc, which tests verify as well. The layout follows the intrinsic sizes of the cards, and the controls of the form and the text cursor are the same during a hover and a resize.

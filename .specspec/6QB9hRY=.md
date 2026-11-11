---
id: 6QB9hRY=
type: requirement
parents:
- B87C_kI=
---
# Fill cards from one exact palette in the distance, type and revision modes

`graph-model.js` holds the one palette `RAINBOW_COLORS`: `#bc82c9`, `#7e97e6`, `#1facce`, `#37b390`, `#92a64b`, `#ca8d3e`, `#dc7b7c`. Counted from zero, a requirement takes entry 4, an implementation 0, an added node 3, a changed node 1, a removed node 6 and a node whose linked sources changed 5. A node at the positive distance `d` takes entry `(d-1) % 7`, and the manifesto, at distance zero, is gray in the distance and type modes. An unknown path and every neutral state take `#929baa`.

The mode with the stored value `git-revision` is offered as Git/Revision Status and is kept as a preference of the view. A change of the node itself decides its fill before the impact of a changed source does: A is green, M blue, D red, a change of linked sources alone amber and an unchanged node neutral. A view without a comparison is labeled as such and neutral, and the draft of a new node and a draft whose node is gone are shown as neutral drafts. A compact card, an expanded card, a card from an earlier revision and the manifesto take the fill of their kind in this mode as well.

The theme colors of headline and corner letter and the colors and dash patterns of the links have meanings of their own beside the fill. The legend labels the colors that are actually shown, and the editor guide explains the modes and the repetition of the colors. A switch of the mode leaves the form with its draft and text cursor, the DOM of the form, the geometry and the camera as they are.

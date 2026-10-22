---
id: 6QB9hRY=
type: requirement
parents:
- B87C_kI=
- bLBNk80=
---
# Use one exact shared palette for distance, type and revision fills

`graph-model.js` owns `RAINBOW_COLORS`: `#bc82c9`, `#7e97e6`, `#1facce`,
`#37b390`, `#92a64b`, `#ca8d3e`, `#dc7b7c`. Zero-based mappings are Requirement 4,
Implementation 0, Added 3, changed 1, removed 6 and source-changed 5.
For positive distance d use `(d-1) % 7`; manifesto zero is gray in distance/type.
Unknown paths and neutral states use `#929baa`.

Persist `git-revision` as Git/Revision Status. Use direct comparison kinds before
source-only impact: A green, M blue, D red, source-only amber, unchanged neutral.
Missing comparison is explicitly labeled and neutral; new/orphaned drafts have
neutral draft presentation. Compact/expanded historical and manifesto cards use
the selected kind too. The neutral-manifesto white-border rule applies in distance/
type modes; revision cards use hue-emphasizing hover. Title/corner theme tokens and
edge colors/patterns retain independent meaning. Legends label actual colors; the
tutorial explains modes and cycles.
Mode switches keep form/draft/caret, native DOM, geometry and camera unchanged.

---
id: NsFLK9o=
type: requirement
parents:
- XzlIEcQ=
- mAZgRy8=
- bOXyw00=
---
# Let native headline text rasterize at the current camera scale

Remove the permanent will-change: transform hint from the complete graph world.
A permanently promoted/composited transform surface can enlarge cached low-scale
text at high zoom. Retain the existing two-dimensional camera transform, native
DOM headlines/forms, textContent safety, and current font/world sizes; do not
replace headlines with canvas/bitmap text, duplicate overlays, per-node counter-
scales, font-smoothing hacks, or geometry changes.

Do not sacrifice camera anchoring, gesture behavior, form DOM/caret/drafts, hover,
world-size measurement, or minimum-zoom arrows. The lack of a permanent raster hint
is a scoped rendering adjustment, not a guarantee that every browser/OS/device has
identical font antialiasing or optimal large-graph navigation performance.

Verify settled high-zoom text in installed VS Code with computed styles, unchanged
intrinsic geometry/DOM identity, and inspected before/after screenshots at the same
pose. Keep native text legible while retaining lower-zoom and navigation checks.

Origin: a separate rendering conclusion addressing the user's blurry/pixelated
headline observation; browser raster policy is an implementation choice and its
visual verification has platform limits.

---
id: 02a4e457-d709-40af-979c-1216064b1f82
type: requirement
parents:
- a723adc8-d69d-4e60-8b4f-0997ab8f4d1d
- d70cdad5-5e03-4200-ac75-74cf6514e56c
- 2b8a4bbc-d15a-4347-90b4-691abdeefaef
managed_hash: 3ed7359ab283f84720950bd6575a5cce751de268088017357fe379ddf5197355
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

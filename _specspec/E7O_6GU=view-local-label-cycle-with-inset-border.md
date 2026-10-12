---
id: E7O_6GU=
type: requirement
parents:
- DG-JpDc=
- LtROyww=
- bLBNk80=
---
# Draw a six-pixel label ring from transient view memory

Keep a map of preview labels in renderer memory, keyed by node ID and separate
from canonical records, drafts and host.setState. A newly loaded view starts with
no labels; redraw/focus/color-mode/refresh in the same view retain them. Independent
views do not share them. New draft previews may be labeled but reset for each new
draft; do not manufacture permanent label identity or transfer it on save.

Delegate contextmenu from card chrome/headlines to cycle the six named colors
in the user's order and clear on the seventh click. Preserve native context
menus for textarea/input/select, editable content, links and inner buttons; do
not intercept the canvas background or treat right-click as selection/edit/save.
History/removed nodes may be labeled as presentation even when read-only.

Use a 6px solid outline with -6px inset offset and inherited rounding. It visually
covers the normal border equally on all sides, without changing border-box sizes,
ports, routes or forms. Labels retain fixed trial inks independent of semantic/
Git fills; hover does not replace the label ring. Existing unrelated darkening
still applies to the whole node. Preserve a separate keyboard-focus cue. Show
an explicit preview-only/not-saved caveat and accessible text naming the label.

Persistence is likely future work, not an implemented CLI/UI metadata feature.
Verify exact cycle/order, ID independence, redraw retention, reload reset, zero
mutation/state writes, no geometry/caret/camera changes, native menu exceptions,
root/removed/draft/expanded cases and computed equal-width paint in both hosts.
No schema/history migration, approval colors or label backend is introduced.

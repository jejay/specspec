---
id: E7O_6GU=
type: requirement
parents:
- DG-JpDc=
- LtROyww=
- bLBNk80=
---
# Draw view-local label rings inside unchanged card outlines

Keep a renderer-memory map keyed by node ID, separate from persisted drafts and
presentation. Same-view redraw/focus/color-mode/Refresh retains labels; a new view
starts empty. New-draft previews reset on a new draft. Delegate chrome/headline
contextmenu to the six-color cycle and keep native field/link/button/background
menus usable. Historical/removed cards support this transient visualization.

Use a 6px solid outline at -6px offset with inherited type shape, equal around the
border box, plus a separate keyboard-focus cue. Fixed label inks retain their hue
on hover and follow unrelated-card darkening. Show accessible preview-only text.
Canonical files, host state and mutation messages contain ordinary node data;
label entries stay in renderer memory. Geometry, ports, forms and camera stay stable.

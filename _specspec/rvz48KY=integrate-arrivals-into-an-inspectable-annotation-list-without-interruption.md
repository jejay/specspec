---
id: rvz48KY=
type: requirement
parents:
- DG-JpDc=
- YOPhqYc=
- XzlIEcQ=
---
# Select and frame whole spotlights from a toolbar dropdown

The toolbar Spotlights button opens an anchored, context-menu-style dropdown with
one text entry per spotlight, newest first. Each entry shows the spotlight message
and compact time/version-count context. A spotlight can contain multiple colors;
its entry is text-only. The dropdown directly offers whole-spotlight selection,
Clear highlight and confirmed Flush local spotlights. Keep every retained entry
reachable by scrolling in small windows.

Selecting an entry activates all colored node sets in that spotlight together.
Apply the border style first, close the dropdown and frame the exact matching
nodes using the full unobscured canvas, like the existing framing action. Enter
the overview while retaining any focused draft and surrounding graph context.
Selecting the same spotlight again highlights and frames it again. Clear highlight
removes rings explicitly. Opening or dismissing the dropdown preserves the camera
and active spotlight. Escape and outside clicks dismiss it; keyboard navigation
makes each entry reachable. Selection is the action itself, with no expanded
member/details view, search field or captured-text preview flow.

The round red toolbar badge counts new spotlight records since this view last
opened the dropdown. Each addition counts once regardless of colors or members;
zero hides the badge. The first successful load establishes a zero-count baseline;
repeated reads add nothing. Opening clears the count. Arrivals while open count
until the next opening. New cues and counts stay in renderer memory; reload starts
a fresh baseline. Polite live text announces arrivals. Arrivals preserve focus,
caret, drafts, camera, active spotlight, dropdown choice and older entries.

Active spotlight selection is a per-view presentation preference. Exact, changed,
absent and unavailable counts explain version matching compactly. Flush confirms
and rechecks the reviewed list, preserving specification files and unrelated local
data. Both hosts watch independently in working and historical views, with Refresh
and configured polling as fallbacks.

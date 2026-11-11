---
id: rvz48KY=
type: requirement
parents:
- DG-JpDc=
- YOPhqYc=
- XzlIEcQ=
---
# Select and frame comparison spotlights from a toolbar dropdown

The Spotlights button in the toolbar opens a dropdown that is anchored to the button and lists the spotlights as text, newest first: one entry per immutable spotlight with its message, time, comparison and number of nodes. Selecting an entry switches to its comparison, replaces the editable highlights with the IDs of all its nodes, closes the menu and frames those nodes that are available in the target or as deleted nodes of the base, using the full canvas. The view changes to the overview and keeps the draft of a focused node. Selecting the same entry again frames again. Nodes that are missing stay in the highlight set, and a selection that matches no node keeps the camera.

The dropdown offers Create spotlight from highlights, Clear highlight and Flush local spotlights, which asks for confirmation. Keyboard navigation, dismissal by Escape or by a click outside, clamping to the window and scrolling keep every entry reachable. An arrival leaves focus, text cursor, drafts, camera, highlights, the choice in the dropdown and the older entries as they are. A round red badge counts the records that arrived since the dropdown was last opened, and the first load and a reload start the count at zero. Polite live text announces arrivals. The counts and the New marks live in the memory of the renderer.

A warning that the working files have drifted appears visibly outside the closed menu, while the best available nodes are highlighted. An error of the local records keeps the last list, whether or not the graph is valid. Both graph editors watch the events of the store in views of the working files and in comparisons between commits, with Refresh and optional polling as fallbacks. Flush checks the reviewed list again.

---
id: -0ljwrM=
type: requirement
parents:
- qf5-4sc=
- t8RQMdE=
- XzlIEcQ=
- SRsw2W0=
---
# Emphasize incident SVG pairs without changing graph geometry

Keep hovered node identity and its last hover-capable pointer position as transient
webview memory, not canonical metadata, saved drafts, camera preferences, selection,
or an approval/review signal. Match each displayed edge by its full parent/child
IDs: emphasize only immediate incoming and outgoing links, including added/removed
historical relationships and unsaved draft links when displayed.

Use delegated pointer transitions so entering text, buttons, or other descendants
inside the same expanded card does not flicker or clear the emphasis. Touch input
must not leave a sticky hover. Clear on pointer exit/window blur; after layout,
refresh, navigation, or camera movement, reconcile the last pointer position with
the actual card under it rather than retaining a stale node identity.

Toggle one presentation class on each existing curve/filled-head pair and raise
incident pairs above other SVG connections, restoring normal ordering on exit.
Use full opacity and brighter, higher-chroma versions of colored connection ink
in its own hue; bLBNk80= replaces the earlier theme-foreground mix for
added/removed/draft links because it washed out their colors. Normal neutral links
retain theme contrast mixing. Retain semantic classes and camera-compensated dashes;
do not replace every relationship with an ambiguous common Git color. Do not grow
stroke width, arrowheads, glow, or hit areas: existing clearance, minimum screen
strength, tangent joins and routing remain unchanged. The SVG stays non-interactive.

Hover sends no host/CLI messages, changes no world positions or camera, recreates
no edges/forms, and does not consume native text-selection or scrolling events.
Test exact incident membership, both curves and heads, isolated nodes, nested form
transitions, refresh/camera reconciliation, read-only historical and draft links,
Git styling, DOM identity, and unchanged form draft baselines/caret. Verify actual
computed paint and hover behavior in the installed VS Code browser.

Origin: a separate presentation conclusion implementing the user's node-hover
request; contrast mixing, event delegation, hit reconciliation, and SVG ordering
are revisable technical choices rather than extra product requirements.

## Hover-darkening extension

The later user request adds darkening outside immediate displayed relationships.
6MUwTIw= extends this conclusion with a second transient class for non-incident
curve/head pairs and unrelated cards. Existing delegation, hit reconciliation,
incident contrast/order and geometry/form invariants remain. Only the hovered
card and endpoints of incident displayed links stay undarkened; links between
neighbors still darken. This supersedes the earlier contrast-only presentation,
not the user intention or the direction/Git cues.

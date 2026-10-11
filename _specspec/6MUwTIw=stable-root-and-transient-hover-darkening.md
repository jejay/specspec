---
id: 6MUwTIw=
type: requirement
parents:
- pWgqwcQ=
- RlFT4io=
- -0ljwrM=
- qnGsij4=
- YOPhqYc=
---
# Use a neutral root fill and transient one-hop darkening

Choose #d3d3d3 as the manifesto's fixed accent and solid card background, in every
color mode, compact/expanded state and host theme. Use dark root text for contrast;
retain themed Git title/corner colors, native input styles and focus/border cues.
Legends distinguish the neutral manifesto from the continuing non-root palette.
The former generic tinted-fill conclusion now has this explicit root exception.

Interpret connected nodes as the hovered card plus endpoints of its displayed
immediate incoming/outgoing links, matching existing incident-link highlighting,
not an ancestor/descendant closure. Historical, removed, reversed and draft links
count when actually drawn; links between two neighbors still darken unless they
are incident to the hovered node. An isolated hovered card darkens every other
card and all connections. A manifesto unrelated to the hover also darkens: its
base hue stays gray, rather than being exempt from the user's darkening request.

Extend existing delegated transient pointer state with a hover-darkened class on
unrelated cards and curve/head pairs. Use brightness(.45) on cards, not reduced
opacity (which can lighten cards on light backgrounds); mix non-incident edge ink
35% with black 65%, retaining hue, dashes, geometry and paired ordering. Constants
are revisable. Remove all darkening on exit, blur, cancellation or touch. Reapply
membership after redraw even if hovered identity is unchanged; camera changes
continue to hit-test the pointer. Do not save hover, send host mutations, replace
forms or change layout/camera/metrics. No animation or permanent compositor hint.

Verify model colors/legends, exact darkened membership, restoration, unchanged DOM,
drafts/caret and geometry, historical/draft/isolated cases, stationary-pointer
refresh and native controls. Extend shared real-host paint checks for both hosts,
normal/minimum zoom and dark/light theme rendering. Passing bounded local tests
is evidence, not universal accessibility or arbitrary-graph performance proof.

Origin: separate revisable choices implementing the user's two visual requests,
following inspection of the existing shared renderer and 99-test passing baseline.
Use the existing development Python; system Python has no specspec package.
Leave unrelated local settings/artwork untouched; install no Git hooks.

## Superseded solid-root interpretation

The user clarification iktVTRU= rejects the solid pale fill/dark text paragraph
above. xCOHepQ= replaces only that styling with shared tinted fills, theme text
and a white manifesto hover border, and adds roomier expanded text/Git markers.
Its initial all-card white-border choice was also mistaken; bLBNk80=
limits white to the manifesto and strengthens other hovered semantic colors. The fixed
gray semantic accent, truthful legends and transient one-hop darkening remain.
The original solid-root reasoning is retained as history, not a live requirement.

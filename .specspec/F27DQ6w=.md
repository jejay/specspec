---
id: F27DQ6w=
type: requirement
parents:
- 1ev9uZo=
---
# Show both graph editors in README screenshots

After the concept sections the README shows what owners work with: one screenshot of
the VS Code extension and one of the desktop app. Both look at real graphs from an
overview distance, where the canvas, its colors and the Git marks are visible and
card text is secondary. The VS Code screenshot shows this repository's own graph
colored by distance from the manifesto, with the Explorer beside it. The desktop
screenshot shows the example planner while two of its stages are compared, with
deleted and added nodes in their revision colors.

A repository script takes the screenshots. It starts each host in an isolated profile
on an independent project, poses the canvas and captures the window through the
DevTools protocol at twice the display resolution. Retaking a screenshot after an
interface change is one command.

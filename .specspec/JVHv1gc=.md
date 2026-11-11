---
id: JVHv1gc=
type: requirement
parents:
- HlpFtiA=
- FHfnj08=
- pWgqwcQ=
---
# Normalize the influence of each revision onto a continuous ramp from green to red

The influence modes work on one complete revision at a time. They use the influence of a node, which includes the node itself, and the longest path of the node from the manifesto. With `c` the influence of a node and `M` the highest influence of a node other than the manifesto, Absolute influence uses `(c-1)/(M-1)` and Log Absolute Influence uses `log(c)/log(M)`. With `lo` the lowest and `hi` the highest influence among the nodes at the same maximum distance from the manifesto, Relative influence uses `(c-lo)/(hi-lo)` and Log Relative Influence uses `(log(c)-log(lo))/(log(hi)-log(lo))`. The logarithm is the natural one and is applied to each influence before the transformed minimum is subtracted. A linear scale subtracts one from each value, including the two ends of its range.

A denominator of zero gives the value zero, which is green. This is the case in a group whose nodes all have the same influence, in a group of one node and in a graph whose nodes beneath the manifesto are all leaves. The manifesto lies outside the influence scales, with its neutral gray accent and its white border on hover. A node whose path is unknown or blocked by a cycle, the unsaved draft of a new node and a draft whose node is gone are shown neutral.

The normalized value maps continuously onto a ramp with green `#4df884` at zero, yellow `#e8d62c` at one half and red `#ba2208` at one. Between these warm anchors, which resemble the Turbo colormap, the color is interpolated piecewise linearly in sRGB, for the cards and for the legend alike. The palettes of the distance, type and revision modes have their own exact mappings.

In a comparison a node that the target contains takes its counts and its group from the target, and a deleted node takes them from the complete base. This holds whatever the view of a selected node shows, whatever forest places the nodes and whatever union of both sides is drawn. The ranges of the raw counts are built on first use, once for the metrics of a revision, and all four influence modes share them, so that the distance, type and revision modes bear none of their cost. Each view stores which mode is selected, and each of the four modes is a stored value of its own. A switch of the mode leaves the node records, the form with its text cursor and draft, the camera, the positions, the routes and the independent marks of Git and of spotlights as they are. The legend shows the swatch of the manifesto and the two ends of the gradient. The editor guide explains the ranges, the normalization and ties.

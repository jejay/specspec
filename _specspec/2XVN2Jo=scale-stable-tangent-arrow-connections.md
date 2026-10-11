---
id: 2XVN2Jo=
type: requirement
parents:
- qf5-4sc=
- qnGsij4=
- mAZgRy8=
---
# Keep connection strength and arrow joins stable under magnification

Compensate connection stroke width in camera space so its visible strength never
falls below a modest screen-pixel floor. Keep an arrowhead large enough to show
direction at low zoom as well, without increasing node sizes or relayouting the
graph. Preserve Git stroke colors and distinct visible dash patterns.

Connect directly to card boundaries without circular socket decorations. Preserve
curved obstacle-aware routes. Distribute attachments over intrinsic card height,
including expanded forms, instead of bunching every edge near the title band.
Reserve a smooth horizontal settling approach
before each rightward arrow. The approach must cover the largest zoom-compensated
head within the supported camera range. Match the final curve tangent to that
approach; terminate the stroked line at the head base and fill the head toward the
target. Leave a short horizontal departure at the source so a zoom-strengthened
steep curve does not brush back through its originating card. This avoids a tight final bend under a straight triangle and avoids a
constant-width line sticking out beyond the tapered tip.

Camera changes update only edge appearance, not node positions, form DOM, canonical
metadata, or CLI state. Verify minimum effective screen width, low-zoom arrows,
no connector circles, tangent continuity and card clearance in focused/overview
views, including strong curvature and historical reverse relationships.

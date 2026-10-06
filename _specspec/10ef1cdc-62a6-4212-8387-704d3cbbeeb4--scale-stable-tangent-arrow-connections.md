---
id: 10ef1cdc-62a6-4212-8387-704d3cbbeeb4
type: requirement
parents:
- e3494686-5da4-40f5-a622-f823c2e0c9b2
- 1f2e42c3-331f-4c1c-adc7-897f9bf2e004
- d70cdad5-5e03-4200-ac75-74cf6514e56c
managed_hash: 6bc2ddaccbf6d78073fa1bd67eb10751f20a2211c2459285817f1e13be655b3a
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

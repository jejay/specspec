---
id: c2ed5444-b7b2-4c2a-901c-ab1ba64e5e54
type: requirement
parents:
- cbcde9ec-5c0b-480e-9401-cf50a4bfeb96
- 4254f33d-ce29-4e33-830e-28a8edd2a51c
- fbaee7c1-4c20-47ab-afd2-ae0503d428b5
---
# Compact placement without discarding multi-parent relationships

Earliest ranks alone leave Dagre's vertical alignment stretched by distant common
sinks. Compute earliest ranks from every primary parent, then choose one
rank-preceding parent per node, deterministically by ID among equally deep parents,
as a placement backbone. Feed this rank-preserving forest to Dagre for compact
ordering/placement. All canonical and historical relationships remain rendered;
the backbone neither changes parent metadata nor declares a preferred/approved
requirement or a dependency of lesser importance.

Allocate non-backbone forward routes through the nearest clear vertical gaps in
skipped card columns, flattening the lane across each full column before curving
in the empty horizontal gaps. Outer gutters remain fallback corridors and serve
reverse historical links. Choose stable order and clearance margins; this is a
presentation heuristic, not an optimal/crossing-free routing guarantee.

Retain the full-parent rank constraints, intrinsic expanded dimensions, camera
independence, full-height attachments, screen-strength floors, and tangent-aligned
arrow approaches. Test root-neighbor vertical concentration as well as early
columns, with full relationship membership and painted-stroke clearance. No tree,
position, ranking, or choice preference is stored in canonical metadata.


After removing distance badges, use slightly shorter compact cards while opening
intrinsic rank and sibling gaps modestly. The initial tuning is 112-world-unit
card height (was 128), rank gap 140 (was 128), and sibling gap 44 (was 36), with
unchanged compact width and routing clearances. These are revisable implementation
constants, not user-prescribed canonical sizes. Verify two-line headlines and the
remaining badges fit, packing stays compact, and changed gaps preserve painted
curve/head clearance and viewport-independent arrangement.

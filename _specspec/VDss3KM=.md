---
id: VDss3KM=
type: requirement
parents:
- tGpRMLM=
---
# Display valid working context while its Git comparison loads

Initial working views may render a validated working snapshot with an explicit
comparison-loading state, then adopt the fresh HEAD/source comparison. Historical
views load their selected comparison directly. Keep provisional meaning visibly
distinct from completed/unavailable comparison. Preserve newer input, bound document,
focus and camera when later data arrives; reject stale document/view/base results.
A comparison failure leaves usable current context with an explicit unavailable
note, while current-file failure retains marked last-valid context and existing
mutation protections. Native/bootstrap sharing avoids a redundant initial worktree
request. Preserve sequence/full-membership rendering acknowledgements and existing
production operation deadlines. Use normal current reads for mutations.

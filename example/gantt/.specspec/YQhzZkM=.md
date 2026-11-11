---
id: YQhzZkM=
type: implementation
parents:
- BumOqek=
sources:
- path: model.js
  blob: d44e2484dad4c61a8bd3d2c75c3a11ec211578a0
  mode: strict
  ranges:
  - - 1
    - 125
- path: test/model.test.cjs
  blob: 790ca5f43cc48a1c02fc7b11c46013facb3dc988
  mode: strict
  ranges:
  - - 1
    - 116
- path: history/personal-v1.json
---
# Calculate workshop forecasts, baseline snapshots and JSON previews

`model.js` implements the iterative UTC weekday forecast over prerequisites, bounded
normalization, copied baselines that later edits leave unchanged, rows for the current
plan and the baseline, and their differences in calendar days. Saving a task validates
the whole changed plan; removing a task validates that no other task still refers to it.
Import returns a validated version-two preview or the warnings of a version-one
conversion. The model tests cover seeded dependency graphs against an independent
reference, deep bounded graphs, weekend, daylight-saving and leap-year dates, invalid
and cyclic input, unchanged input and baseline, and the archived personal JSON file. The
model is pure and deterministic over local data.

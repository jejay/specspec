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

`model.js` implements iterative UTC weekday DAG scheduling, bounded normalization,
immutable copied baselines, current/baseline rows and calendar-day deltas. Task save
validates the whole candidate; removal validates reference safety. Import returns a
validated version-two preview or explicit version-one conversion warnings.

Model tests cover seeded DAGs against an independent reference, deep bounded graphs,
weekend/DST/leap dates, invalid/cyclic inputs, input/baseline immutability and the
archived personal JSON fixture. The pure model has deterministic local-data semantics.

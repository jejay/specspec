---
id: YQhzZkM=
type: implementation
parents:
- XZk4rMA=
- rrN-aHA=
- BumOqek=
- J3ggsWw=
sources:
- path: model.js
  blob: d44e2484dad4c61a8bd3d2c75c3a11ec211578a0
  mode: strict
  ranges:
  - - 1
    - 125
  symbol: forecast, validate, chart, captureBaseline, previewImport
- path: test/model.test.cjs
  blob: 790ca5f43cc48a1c02fc7b11c46013facb3dc988
  mode: strict
  ranges:
  - - 1
    - 116
  symbol: 20 model regressions and seeded DAG reference
- path: history/personal-v1.json
  symbol: actual archived stage-two export
---
# Implement validated forecasts and immutable what-if baselines

model.js implements iterative UTC weekday DAG forecasting, duration/earliest bounds, reference/cycle validation, bounded dates/task counts/horizon, copied baseline snapshots, added/removed comparisons, explicit calendar-day deltas, safe deletion, and versioned JSON preview/conversion. Twenty Node tests passed, including forty seeded DAGs against an independent reference, deep bounded graphs, DST/leap/weekend bounds, baseline/input immutability, and the real archived personal v1 export. No owner/resource leveling, holiday calendar, cloud, or optimization is implemented. V1 conversion deliberately changes end/weekend semantics and drops priorities; warnings are data returned before Apply.

---
id: GkhgCJI=
type: implementation
parents:
- ZkyH8qI=
- eVTiiqY=
- w3weBig=
- s3jaP8o=
sources:
- path: model.js
  symbol: forecast, validate, chart, captureBaseline, previewImport
- path: test/model.test.cjs
  symbol: 20 model regressions and seeded DAG reference
- path: history/personal-v1.json
  symbol: actual archived stage-two export
---
# Implement validated forecasts and immutable what-if baselines

model.js implements iterative UTC weekday DAG forecasting, duration/earliest bounds, reference/cycle validation, bounded dates/task counts/horizon, copied baseline snapshots, added/removed comparisons, explicit calendar-day deltas, safe deletion, and versioned JSON preview/conversion. Twenty Node tests passed, including forty seeded DAGs against an independent reference, deep bounded graphs, DST/leap/weekend bounds, baseline/input immutability, and the real archived personal v1 export. No owner/resource leveling, holiday calendar, cloud, or optimization is implemented. V1 conversion deliberately changes end/weekend semantics and drops priorities; warnings are data returned before Apply.

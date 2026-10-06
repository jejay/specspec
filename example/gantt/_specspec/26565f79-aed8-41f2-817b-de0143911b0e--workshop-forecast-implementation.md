---
id: 26565f79-aed8-41f2-817b-de0143911b0e
type: implementation
parents:
- fc2a2b2f-a7b0-4980-87d9-4f57101445a2
- 24a54dea-6e0b-4a6c-8f62-4f760769dc5d
- adc104a8-f8dc-40dc-b27b-c1a01351c1f8
- 928060fa-c02d-46dd-b823-b002bcf41353
sources:
- path: model.js
  symbol: forecast, validate, chart, captureBaseline, previewImport
- path: test/model.test.cjs
  symbol: 20 model regressions and seeded DAG reference
- path: history/personal-v1.json
  symbol: actual archived stage-two export
managed_hash: 6b772e885f461f1604b773030985a671d6ffbd08321fd4b4ce1254c5bad59942
---
# Implement validated forecasts and immutable what-if baselines

model.js implements iterative UTC weekday DAG forecasting, duration/earliest bounds, reference/cycle validation, bounded dates/task counts/horizon, copied baseline snapshots, added/removed comparisons, explicit calendar-day deltas, safe deletion, and versioned JSON preview/conversion. Twenty Node tests passed, including forty seeded DAGs against an independent reference, deep bounded graphs, DST/leap/weekend bounds, baseline/input immutability, and the real archived personal v1 export. No owner/resource leveling, holiday calendar, cloud, or optimization is implemented. V1 conversion deliberately changes end/weekend semantics and drops priorities; warnings are data returned before Apply.

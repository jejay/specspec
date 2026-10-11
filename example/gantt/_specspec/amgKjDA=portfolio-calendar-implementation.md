---
id: amgKjDA=
type: implementation
parents:
- 046joRU=
- mS49hpI=
sources:
- path: model.js
  symbol: forecast and rollups
- path: test/model.test.cjs
  symbol: six prototype model tests
retired: true
---
# Implement the local portfolio forecast experiment

model.js computes validated UTC weekday finish-to-start dates and simple project rollups. Six Node tests passed for the demo, weekend boundaries, order independence, bad dates/durations/IDs/progress, cycles/missing links, and rollup semantics. Named owners are only displayed: there is NO resource leveling or shared service. This prototype is not production scheduling. Browser presentation has not yet been exercised by an automated real-browser check.

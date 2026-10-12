---
id: NEuKpqM=
type: implementation
parents:
- 9tL5xM8=
- uEwiGLE=
sources:
- path: model.js
  blob: a4020a2cef0d227f6974b0b9518d9f49f7be6a51
  mode: strict
  ranges:
  - - 1
    - 50
  symbol: forecast and rollups
- path: test/model.test.cjs
  blob: 91c8c463a97598f684d068b6b52659faf749e4e8
  mode: strict
  ranges:
  - - 1
    - 29
  symbol: six prototype model tests
retired: true
---
# Implement the local portfolio forecast experiment

model.js computes validated UTC weekday finish-to-start dates and simple project rollups. Six Node tests passed for the demo, weekend boundaries, order independence, bad dates/durations/IDs/progress, cycles/missing links, and rollup semantics. Named owners are only displayed: there is NO resource leveling or shared service. This prototype is not production scheduling. Browser presentation has not yet been exercised by an automated real-browser check.

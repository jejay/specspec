---
id: 006fd979-8651-4c7b-8627-c5ade1ca0b57
type: implementation
parents:
- beb1f8f3-aafe-4f77-83fb-9d1ffc9b3baa
- a8a584cd-1ed6-4b4d-a944-c56979f57632
sources:
- path: model.js
  symbol: forecast and rollups
- path: test/model.test.cjs
  symbol: six prototype model tests
managed_hash: 0895200a42916e31f3ec58bb070299af5ea383ec007de9963a9216a78ce63508
retired: true
---
# Implement the local portfolio forecast experiment

model.js computes validated UTC weekday finish-to-start dates and simple project rollups. Six Node tests passed for the demo, weekend boundaries, order independence, bad dates/durations/IDs/progress, cycles/missing links, and rollup semantics. Named owners are only displayed: there is NO resource leveling or shared service. This prototype is not production scheduling. Browser presentation has not yet been exercised by an automated real-browser check.

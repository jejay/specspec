---
id: 6006dc63-84fe-4aba-ac7a-0c6144536f61
type: implementation
parents:
- 7a6014c1-9e6b-4bd8-87f7-f365f5b0765a
- a237a71f-db85-4bf8-a20a-2287be08c28b
sources:
- path: model.js
  symbol: validate, span, personal demo
- path: test/model.test.cjs
  symbol: seven manual-plan tests
- path: history/personal-v1.json
  symbol: real version-one demo export
managed_hash: 683503c6edb8704663f8ff0f3e3afec2c4a70ec272939aef2d23527bf28b5822
retired: true
---
# Implement independent inclusive calendar dates

model.js validates the version-one envelope, inclusive calendar ranges/priorities, IDs, title/date bounds, and a 730-day horizon. Seven actual Node tests passed, including weekend and same-day ranges, order-independent manual edits, JSON round-trip, invalid data, literal project text, and no input mutation. No duration propagation, prerequisites, owners, portfolio aggregation, resource scheduler, or hosted service remains. history/personal-v1.json is exported from the running model demo for the later conversion exercise.

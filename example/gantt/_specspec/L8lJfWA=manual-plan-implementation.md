---
id: L8lJfWA=
type: implementation
parents:
- jZSWWYU=
- BiO5kxc=
sources:
- path: model.js
  blob: 465b97059b17683083473b5bde10b1073a2e2c67
  mode: strict
  ranges:
  - - 1
    - 36
  symbol: validate, span, personal demo
- path: test/model.test.cjs
  blob: 55fa973361baa54ba4984b6cadc0c78b490e2133
  mode: strict
  ranges:
  - - 1
    - 11
  symbol: seven manual-plan tests
- path: history/personal-v1.json
  symbol: real version-one demo export
retired: true
---
# Implement independent inclusive calendar dates

model.js validates the version-one envelope, inclusive calendar ranges/priorities, IDs, title/date bounds, and a 730-day horizon. Seven actual Node tests passed, including weekend and same-day ranges, order-independent manual edits, JSON round-trip, invalid data, literal project text, and no input mutation. No duration propagation, prerequisites, owners, portfolio aggregation, resource scheduler, or hosted service remains. history/personal-v1.json is exported from the running model demo for the later conversion exercise.

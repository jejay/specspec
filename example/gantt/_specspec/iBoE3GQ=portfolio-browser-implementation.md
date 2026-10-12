---
id: iBoE3GQ=
type: implementation
parents:
- -L-81g0=
- tVx6V-E=
- 7cemSLY=
- T2iwdAI=
sources:
- path: index.html
  blob: b2701c841d208a5c50df5ee6da51e9eea8ee6fba
  mode: expanding
  ranges:
  - - 1
    - 9
  symbol: portfolio table and chart
- path: app.js
  blob: 7f45278b74ffa2b2f0dc0c690244b3d5f7616e88
  mode: expanding
  ranges:
  - - 1
    - 19
  symbol: text-only demo rendering
- path: styles.css
  blob: 3f2037c1609c7c7f558027939af44f30606db98b
  mode: expanding
  ranges:
  - - 1
    - 11
  symbol: scrolling chart
- path: package.json
  symbol: dependency-free test command
retired: true
---
# Show the read-only portfolio in a local browser

index.html, app.js and styles.css render a local read-only portfolio timeline and date table using native text and locally loaded scripts. No accounts, persistence, external requests, editing, or capacity optimization is implemented. JS syntax and six model tests passed; full browser interaction is not claimed. Open index.html directly, or serve this folder locally.

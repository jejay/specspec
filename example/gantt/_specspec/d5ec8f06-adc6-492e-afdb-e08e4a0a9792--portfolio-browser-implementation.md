---
id: d5ec8f06-adc6-492e-afdb-e08e4a0a9792
type: implementation
parents:
- cb024fe9-de72-4b31-87d6-4d461c8b370c
- 928060fa-c02d-46dd-b823-b002bcf41353
- ac3d8b1d-980e-4c16-be96-ed1a61f02972
- aa4e41fe-22f4-464a-8295-ba7dd1fef7f5
sources:
- path: index.html
  symbol: portfolio table and chart
- path: app.js
  symbol: text-only demo rendering
- path: styles.css
  symbol: scrolling chart
- path: package.json
  symbol: dependency-free test command
managed_hash: 05c3643adc2be567cdf3c5293475c0337054c7b8a83eaef2a2a1d39487590fa1
retired: true
---
# Show the read-only portfolio in a local browser

index.html, app.js and styles.css render a local read-only portfolio timeline and date table using native text and locally loaded scripts. No accounts, persistence, external requests, editing, or capacity optimization is implemented. JS syntax and six model tests passed; full browser interaction is not claimed. Open index.html directly, or serve this folder locally.

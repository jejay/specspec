---
id: m8kx_4A=
type: implementation
parents:
- oo28JzE=
- BumOqek=
sources:
- path: index.html
  blob: fb33e08a494d78c216e0e978f79dda7b0ff00889
  mode: expanding
  ranges:
  - - 1
    - 45
- path: app.js
  blob: d6cb272cff8b176d349ad88623810e089028917b
  mode: expanding
  ranges:
  - - 1
    - 146
- path: styles.css
  blob: 863aaa11314150aadc70da1660600b644c8bf005
  mode: expanding
  ranges:
  - - 1
    - 21
- path: test/browser.cjs
  blob: 2ad56e0dd5374911fab412c3e67cde5794f3d95b
  mode: expanding
  ranges:
  - - 1
    - 162
- path: package.json
---
# Edit and persist a native local workshop calendar

`app.js`, local markup and styles implement current/baseline bars, date table,
weekend shading, editable prerequisites and explicit baseline capture/replace/clear.
Valid edits autosave. Corrupt/v1 saved bytes remain downloadable and protected
until Apply/reset. Import preview and cancelled/stale reads retain saved work.
Dirty failed drafts and native caret persist through invalid edits and resize.

Project strings use textContent. Real-browser checks cover forecasts, baselines,
cyclic drafts, safe task deletion, literal markup, downloads/uploads, conversion
preview/cancel/Apply, reload, protected/denied storage and direct-file launch. Model
and browser seams provide reproducible bounded checks for this local planner.

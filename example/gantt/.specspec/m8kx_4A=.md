---
id: m8kx_4A=
type: implementation
parents:
- oo28JzE=
- BumOqek=
sources:
- path: index.html
  blob: 0453dab8152586cebaf97be54b24293d3f570a87
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

`app.js`, the local markup and the styles implement current and baseline bars, the date
table, weekend shading, editable prerequisites and the explicit capture, replacement and
clearing of the baseline. Valid edits are saved automatically. Corrupt or version-one
bytes in storage can be downloaded and stay protected until Apply or reset. An import
preview and a cancelled or overtaken file read leave the saved work as it is. A failed
draft and the caret stay in place through invalid edits and resizing. Project strings
are set through textContent. Tests in a real browser cover forecasts, baselines, cyclic
drafts, safe removal of tasks, literal markup, downloads and uploads, conversion preview
with Cancel and Apply, reload, protected and denied storage, and a start directly from
the file. The model tests and the browser tests are repeatable checks of this local
planner.

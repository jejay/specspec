---
id: Pds9RwY=
type: implementation
parents:
- rAMkhAg=
- iiyuP94=
- w3weBig=
- wJjj5WU=
sources:
- path: index.html
  symbol: accessible native forms, chart/table, import controls
- path: app.js
  symbol: local editor, baseline, protected autosave, import preview
- path: styles.css
  symbol: responsive panels and locally scrolling native timeline
- path: test/browser.cjs
  symbol: isolated real Chromium UI/file/storage smoke test
- path: package.json
  symbol: zero-install test scripts
---
# Implement a native local Gantt editor with real browser evidence

Classic local scripts and native forms render current/baseline bars, a textual date table, weekend shading, editable prerequisites, and explicit baseline capture/replacement/clear. Valid edits autosave; corrupt/legacy saved bytes stay protected until explicit Apply/reset and can be downloaded unchanged. File and pasted JSON preview does not mutate the plan; stale file reads are cancelled. Dirty failed task drafts survive invalid cycles and cancelled navigation; resizing retains native caret/form identity and confines horizontal scroll to chart/table. Imported names use textContent. Twenty model tests, syntax checks, and a real installed Windows Chromium smoke test passed; desktop/narrow screenshots were inspected. Real browser checks exercised forecast changes, immutable baseline, cyclic drafts, safe deletion, literal markup text, actual download/file upload, preview/cancel/lossy v1 conversion, reload, protected/corrupt/legacy storage, storage denial, and direct file-origin launch. No external app requests occurred (native data-URL date icons are not network requests). This is dispatched browser evidence, not exhaustive manual/accessibility/platform/performance or production certification.

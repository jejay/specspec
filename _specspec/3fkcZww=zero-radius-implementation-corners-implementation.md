---
id: 3fkcZww=
type: implementation
parents:
- AZbsoEA=
sources:
- path: graph-ui-common/media/graph.css
  symbol: zero-radius Implementation cards
- path: graph-ui-common/test/graph.test.cjs
  symbol: compact/expanded 0px expectation
- path: graph-ui-common/test/graph-model.test.cjs
  symbol: zero-radius sideBoundary checks
- path: graph-ui-common/test-host/ui.cjs
  symbol: 0px real-host checks and square collision oracle
- path: docs/own-spec.md
  symbol: zero-radius correction and current evidence
---
# Apply the user's exact zero-radius Implementation correction

Implement ejSVfuc= through revised AZbsoEA=: .card.implementation now has
border-radius: 0px, in compact and expanded views. The former 7px choice remains
history in YHSK9DA=. Requirement 24px, manifesto circles, sizes/native form budget,
palettes/mappings, hover/labels and persistence remain unchanged. No routing,
backend, node schema or maintained-history change is needed.

Update the DOM and real-host type-radius expectations to 0px. Extend pure outline
checks for zero radius at top/near-corner/middle/bottom heights. Fix the independent
real-browser collision oracle's zero-radius branch: after its inset bounding check,
a square contains the point. Applying the rounded test distance < radius-1 to
radius 0 would incorrectly classify the entire Implementation interior as empty.
An explicit center-inside/exterior-outside guard prevents that false-positive
collision check. This strengthens verification; production routing is unchanged.

Actual checks passed: 131 shared UI, 34 VS Code adapter and nine Electron unit
tests; Ruff lint/format and working/root and Gantt snapshot validators. Both host
assets were rebuilt. Complete Electron host checks passed with the expanded-square
Implementation screenshot inspected. The combined build/unit/Electron/VS Code
command hit its 300-second outer tool deadline after VS Code's shared UI passed
but before its native-document suite completed. An unchanged standalone VS Code
rerun passed the complete shared/native suite. Both VS Code logs include a startup
mutex warning, not an assertion failure. No internal timeout/assertion or production
camera behavior was changed. Python/backend and standalone playground suites were
not rerun for this CSS-only correction; their preceding shape run remains history,
not a fresh zero-radius result. Logs/images remain ignored bounded local evidence.

Refresh current guides and specification, preserve earlier choices/check counts
as history and unrelated existing checkout edits. Stage only this intended slice,
validate the exact index and commit. No new hook, persistence or approval gate.

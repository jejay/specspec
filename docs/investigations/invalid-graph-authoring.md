# Invalid-graph authoring verification

This change separates explicit file edits, structural validity, analysis completeness
and potential reasoning effects. The [workflow guide](../invalid-graphs.md) documents
exact deletion, issue reads, contextual diffs, intermediate edits, final-validity
checks and coherent batches. [The specification tour](../own-spec.md#exact-deletion-invalid-working-graphs-and-head-views)
links the owner intention, revisable choices and implementation mappings.

## Evidence and boundaries

- The complete Python suite passes: **581 tests** in the final run. Coverage includes
  original valid behavior plus exact/shared/exclusive/
  deep deletion, retained bytes/references, invalid reads, raw/current/staged/history
  views, unavailable material, finite cycles and scoped metrics, contextual causes,
  batch aliases/conflicts/body files/consent, independent safety and invalid recovery.
- Shared UI: 254 tests; VS Code adapter: 46; Electron adapter: nine. Native repair
  regressions preserve actual empty-body and partial source input separately from
  canonical membership. Managed malformed targets remain unsavable, with raw access.
- Complete installed Windows Electron and VS Code host suites pass against disposable
  independent Gantt clones. Both retain exclusive/shared/deep/staged/new conclusions
  after deleting one parent, display the actual invalid graph, save explicit parent/
  body repairs through real forms, and check the exact coherent index before commit.
- Full host suites also retain historical source/spotlight, all eight color modes,
  literal/inline editing, Ctrl+S, layout/camera/hover, watcher/draft/caret and HEAD/D
  lifecycle probes. Electron checks sandbox/network boundaries and persisted reload.
  VS Code checks actual native Save/undo/redo, raw/split synchronization, empty-body
  repair, CRLF/Unicode and independent node tabs.
- The final shared host phases took about 174 seconds (Electron) and 265 seconds
  (VS Code, concurrent with Python). Existing per-operation and aggregate guards
  were retained. These are observations, not production responsiveness guarantees.
- The entire maintained Gantt history was rebuilt externally through 123 actual
  API-7 CLI executions, retaining all eight commits/tags, historical identities,
  meaningful redirects, runnable app bytes and staged source retention. All retained
  revisions validate; snapshot, actual receipts, ledger and bundle match. Existing
  manual clones and unrelated specspec history were preserved.
- Working/exact-index graph and source checks, Ruff, format checks and Git whitespace
  checks validate the committed slice. Canonical node schema remains format 7.

## Issues found during verification

The first Electron attempt passed the new exact-deletion/UI-repair phase, then
exposed a missing invalid-state banner on a retained unreadable draft. The draft
notice had overwritten the graph diagnostic prefix and mislabeled unreadable
content as deleted. One shared note path now preserves both meanings; a dedicated
DOM regression and the complete host reruns pass.

The first VS Code attempt passed the shared UI phase, then timed out at the old
native invalid-buffer probe. Fresh invalid-state reads revealed that empty native
bodies needed separate repair-form fields rather than old canonical text. The
backend now returns those actual bounded native fields separately, and the renderer
preserves editable input without claiming canonical membership. Native unit and
installed checks now assert the fresh invalid graph, actual empty input, repair,
Save and split behavior, rather than requiring a stale-view notice.

All failed-run logs and isolated diagnostic profiles remain available locally;
passing reruns are evidence of these specific corrections, not universal stability.
Useful logs under `.specspec/local/` include `invalid-full-python-final-2.log`,
`invalid-common-native-repair.log`, `invalid-vscode-host-final.log`,
`invalid-electron-host-final.log`, `invalid-commit-python-final.log` and the
`invalid-authoring-history/` reconstruction. Final focused follow-ups additionally
cover non-Git contextual evidence, unreadable-file spotlight drift and honest
non-writing preview labels, unreadable endpoint labels and dangling-ID allocation
protection through Python/adapter regressions; the installed-host
runs qualify the shared graph/native repair implementation.

Linux and physical macOS execution were not qualified here. File notifications,
concurrent raw editing, power-loss durability, arbitrary graph density and semantic
justification still require their own assessment. No release publication or owner
hook installation was performed.

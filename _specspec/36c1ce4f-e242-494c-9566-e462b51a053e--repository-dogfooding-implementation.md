---
id: 36c1ce4f-e242-494c-9566-e462b51a053e
type: implementation
parents:
- 407b1a12-8984-4c99-9b7f-b920da33e31b
- 955b905a-6220-4d5c-b0ca-fab86b6b6db8
- ca580dc7-c7fa-48bc-91b1-59243144a0bf
sources:
- path: .github/workflows/ci.yml
- path: .vscode/launch.json
- path: .vscode/tasks.json
- path: AGENTS.md
- path: README.md
- path: docs/node-canvas.md
- path: docs/own-spec.md
- path: specspec-dev.code-workspace
- path: tests/test_repository_spec.py
- path: vscode/.vscode/launch.json
- path: vscode/scripts/build-webview.cjs
- path: vscode/test-host/run.cjs
- path: vscode/test-host/smoke.cjs
- path: vscode/test-host/ui.cjs
- path: tests/test_migration.py
  symbol: legacy conversion and cross-version verification
- path: tests/fixtures/README.md
  symbol: original tool-managed compatibility data
managed_hash: d1e937e709a7bd241e7f77304b03bd3f9abb8d1c09ca1fa15e1b5725cdeb6dc4
---
# Check and document this repository's approval-free graph

The Python CI matrix validates this repository graph with warnings as failures.
Repository tests inspect real nodes/context, unmanaged-edit detection, and staged
copies in disposable repositories without freezing IDs, counts, or design choices.
The working graph records the user's risk-proportionate review intention separately
from the technical schema/migration conclusion. The old approval workflow, v1 schema,
and unimplemented approval-receipt candidate are withdrawn, with history retained.

The 48-node graph was migrated through the fingerprint-guarded CLI, not a Markdown
rewrite or ad hoc hash refresh. Verification checked stable identities, body text,
parent links, source references, extensions, and withdrawal during conversion.
README, CONCLUSION_SPEC.md, the graph tour, and AGENTS.md now describe review until
an implementation attempt is worth its risk/token budget, not individual node
sign-offs. INTENTION_SPEC.md and the original LICENSE remain unchanged.

68 Python tests, 70 editor tests, TypeScript compilation, Ruff, and graph validation
with warnings as errors passed locally. Tests exercise original v1 fixtures,
strict v2 metadata, migration interruption/recovery, old/new Git snapshots,
removed acceptance commands/actions, sibling context, and draft/history/trust guards.

Installed VS Code/Chromium on Windows rendered 48 nodes and passed approval-free
controls, withdrawal labels, distance/type palettes, earliest source ranks, compact
origin placement, minimum-zoom stroke/head strength, tangent joins, complete edge
membership, multiple-depth parents, native gestures, independent cameras, and
resized painted-stroke clearance. Screenshots were captured and inspected. Normal
development launches retain trust; only the isolated automated host disables it.

Remote CI, publication, and full manual mutation/revision-picker workflows remain
unverified. Process recovery is not full power-loss durability, source symbols are
not language-resolved, and rendering is not virtualized or universally optimal.
Implementation evidence informs the next iteration rather than making choices permanent.

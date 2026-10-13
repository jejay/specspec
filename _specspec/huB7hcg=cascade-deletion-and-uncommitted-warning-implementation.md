---
id: huB7hcg=
type: implementation
parents:
- AuhoBoU=
- PfJv45U=
sources:
- path: src/specspec/deletion.py
  symbol: deletion_plan, deletion_warnings
- path: src/specspec/workspace.py
  symbol: delete_nodes, mutate, recover
- path: src/specspec/cli.py
  symbol: delete, read_deletion_plan
- path: src/specspec/git.py
  symbol: repository_paths, run_git
- path: graph-ui-common/host/session.cjs
  symbol: GraphSession.handle delete preview/confirmation
- path: graph-ui-common/host/documents.cjs
  symbol: ProjectDocuments.mutate dirty-document guard
- path: graph-ui-common/media/graph.js
  symbol: updateButtons descendant-deletion title
- path: graph-ui-common/view.cjs
  symbol: Delete node and descendants control
- path: vscode/test-host/budgets.cjs
  symbol: PHASE_GUARD_MS, HOST_GUARD_MS
- path: tests/test_cascade_deletion.py
- path: tests/test_deletion.py
- path: tests/test_core.py
- path: tests/test_transactions.py
- path: tests/test_ids.py
- path: graph-ui-common/test/session.test.cjs
- path: graph-ui-common/test/graph.test.cjs
- path: vscode/test/extension.test.cjs
- path: vscode/test/budgets.test.cjs
- path: graph-ui-common/test-host/platform.cjs
- path: vscode/test-host/run.cjs
- path: vscode/test-host/smoke.cjs
- path: vscode/test-host/documents.cjs
- path: electron/test-host/run.cjs
- path: example/gantt/history/verify.py
- path: example/gantt/history/gantt.bundle
- path: docs/deletion.md
- path: docs/native-editors.md
- path: docs/architecture.md
- path: docs/architecture.svg
- path: docs/own-spec.md
---
# Implement full/shared descendant deletion and pre-write uncommitted warnings

Realize fuyy0Lk= via AuhoBoU=, with PfJv45U= as the separately justified host-test
budget choice. 5d5oDCM= is amended; JqNzSPg='s earlier named-files-only behavior is
historical. Format/API 5 and canonical node/source schema are unchanged. No root
conversion, obsolete reader or example-history rewrite is needed for this behavior
extension. No status, node fingerprint, approval or reparenting mechanism is added.

New deletion.deletion_plan traverses the saved graph iteratively with one visited
set over requested roots. Every reachable child belongs, including multiple-parent
children with surviving outside parents, their deeper descendants and overlapping
paths/roots. Each file is removed once. Outside parents/ancestors/unrelated nodes
remain byte-identical. Manifesto/unknown/empty/duplicate requests and invalid graphs
are rejected before canonical writes. Layout backbones, all-parent ownership, source
impact and HEAD/display-union relationships do not determine deletion membership.

The plan checks every affected canonical path via NUL-delimited ordinary Git status,
with literal nested-project paths, no optional Git locks/index refresh and fsmonitor
disabled. Warnings cover untracked/ignored or staged additions, staged/unstaged
changes, raw comment-only changes, renames, mode/index conflicts; staging is not
committing. Git's line-ending/clean-filter interpretation applies. Source-code-only
changes do not warn about unchanged node files. Non-Git/failed assessment explicitly
warns for the entire scope rather than asserting it committed; unborn nodes warn.
Git flags/configuration can hide changes: no universal/adversarial detection claim.

CLI delete --dry-run is non-writing and returns requested_ids/deleted_ids, ID/path
pairs, per-node statuses and assessment/warning details. Normal human terminal
warned deletion asks one whole-action confirmation; JSON/noninteractive calls with
warnings refuse to mutate without --yes. Confirmed --yes still emits stderr warnings
BEFORE unlinking; JSON stdout is one envelope retaining warning diagnostics. Success
changed_ids/deleted_ids/affected reports the complete removed set, not just arguments.
Library delete_nodes similarly exposes warned confirmation or explicit consent.
Cancel/refusal leaves canonical files unchanged and no unfinished journal.

Shared GraphSession previews with the same CLI, confirms total file count/shared
children and per-node warnings, then submits --yes --reviewed-plan with bounded JSON
stdin. The managed writer replans under the ordinary lock and compares scope, paths
and warning/assessment records directly before writing. Changed scope/new warnings
fail with DELETE_PLAN_CHANGED; no enlarged-cascade retry. This is transaction consent,
not --expect, hashes or approval receipts, and does not freeze every text byte/HEAD.
Existing original-byte checks, null-replacement journals and recovery cover all
implicit descendants too. Recovery refuses new external text. Native pending edits
are drained, action stays bound, project-wide dirty documents (including descendant
tabs) remain protected, and absent buffers cannot resurrect files. Both hosts share
this behavior; button/title explicitly describe descendants. No automatic source
file deletion, staging, commit, hook or Git object/ref/index write.

HEAD-relative default ghosts retain every committed deleted descendant through
staging, and disappear after commit; a never-committed descendant has no fabricated
base ghost. Both full Windows host graph suites verified an actual saved branch
with sole-parent children and two shared descendant levels over the independent
maintained Gantt history: staged/deeper and new-child warnings, physical deletion,
unchanged outside-parent bytes, all D ghosts through staging, all gone after commit,
via Git/file notifications with no Refresh/default polling. Full Electron passed.
Final fresh combined VS Code passed shared AND native document checks. Existing
color/shape/ink/camera/source/native document assertions remain unchanged.

Actual checks: 182 Python (25 new cascade cases), 141 shared UI, 37 VS Code adapter/
harness and nine Electron tests; Ruff lint/format, working root/Gantt validation,
complete unchanged eight-revision Gantt verifier with 123 actual API-5 receipts and
all historical model/source/index checks. Old receipts remain actual earlier calls,
not fabricated new executions. Maintained deleted batches remain valid closures.
No new schema means no corpus rekey/reconstruction; existing manual clones,
experiments/backups and diagnostic profiles are preserved.

Retain observed failures/limits: initial pre-format lint found long lines; formatting
and explicit string splits passed. Initial focused 89 tests passed; an added unmerged
fixture test then failed among 92 because its Git helper returned bytes, accidentally
writing b'...' object IDs to index-info. ASCII decoding fixed that test setup; all
182 tests passed later. First shared/adapter/Electron unit suites passed. Initial
full VS Code run and unchanged retry passed cascade/shared UI, but their existing
240-second outer timer killed native checks at different-node-tab. Unchanged native-
only passed. PfJv45U= chooses one tested shared budget module: preserve both 160s
phase guards and all individual operation deadlines/assertions, align outer guard
to 360s (sum plus startup/shutdown). Fresh combined passed. This identifies the timer
mismatch, not an exclusive cause for all past host scheduling failures or a production
speed guarantee. Expected invalid-file recovery errors remain in host logs.

Updated deletion/native/conclusion/engineering guides. Corrected an overlooked stale
retirement sentence in the architecture SVG from the preceding deletion task; it
was documentation, not a runtime flag, and original branding/source art is untouched.
Source references and affected earlier implementation explanations link the current
choice while retaining earlier counts/failures as history. Tests and real-host runs
are bounded dispatched evidence, not semantic proof, remote CI, every-platform/theme,
filesystem-atomic deletion, all-event delivery or adversarial safety certification.

A later annotation script hit its 30-second outer tool deadline after creating this
record and updating six earlier records, leaving a stale lock before the last
annotation's journal/write. The recorded writer PID 37032 was checked absent in
the Windows process list (the other Python process was unrelated); explicit
recover --force-lock cleared the stale state, then the missing annotation completed.
Original recovery/diagnostic files were retained; final graph validation passed.

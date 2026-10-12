---
id: EpO6sR4=
type: implementation
parents:
- YaXJpGE=
- 3fWBW_g=
sources:
- path: example/gantt/history/gantt.bundle
  symbol: complete current-schema standalone Git history
- path: example/gantt/history/revisions.json
  symbol: actual stage commit IDs and receipt ordinals
- path: example/gantt/history/cli.jsonl
  symbol: 123 actual current CLI executions
- path: example/gantt/history/verify.py
  symbol: clone_history, verify
- path: example/gantt/history/WALKTHROUGH.md
- path: example/gantt/README.md
- path: example/gantt/AGENTS.md
- path: tests/test_gantt_example.py
- path: tests/test_gantt_git.py
- path: tests/test_repository_spec.py
  symbol: present-working-graph checks only
- path: graph-ui-common/test-host/fixture.cjs
  symbol: structural fixture node selection
- path: vscode/test-host/run.cjs
  symbol: maintained Gantt canvas and compact native-document fixtures
- path: electron/test-host/run.cjs
  symbol: maintained Gantt canvas fixture
- path: example/gantt/test/browser.cjs
  symbol: installed Chromium smoke
- path: example/gantt/history/checkout.py
  symbol: safe independent workspace creation
- path: tests/test_example_checkout.py
  symbol: non-destructive checkout/identity checks
---
# Rebuild the Gantt regression history with actual current CLI operations

## External-workspace correction

TAvql3w= and 83D9YWw= clarify that the tracked example/gantt snapshot is not a Git
workspace. Git there selects SpecSpec development commits, explaining the user's
UI failures against obsolete schemas. The safe checkout helper creates independent
manual workspaces and disposable test clones. Both host fixtures now retain the
complete maintained stage history, rather than copying files into one new baseline
commit. CI application/browser checks run in a clone; all retained refs and final
runtime/test snapshot consistency are checked. The history walkthrough documents
recurring whole-history reconstruction on every schema change and optional fiction.
The separate oFOaAVo= implementation record describes current verification; earlier
run counts and reconstruction evidence below remain historical, not repeated claims.

The maintained Gantt project history is now an independent complete Git bundle,
not a demand to parse the surrounding SpecSpec repository's older graph revisions.
It contains eight real commits: empty predecessor, three spec/code pairs, final
audit. Actual current CLI executions regenerated all 44 node IDs, with one mapping
retained across every snapshot, and produced 123 new API-3 receipts without hashes
or --expect. Reconstruction is labeled honestly rather than passed off as untouched
original evidence. Application code/fictional redirects remain; the workflow
evidence node and current README/agent/history guides describe the new contract.
No unrelated SpecSpec commits were rewritten and no nested .git/hook was installed.

The verifier reconstructs receipt contents, checks actual full ancestor/impact
reads, clones the portable bundle with explicit LF checkout settings, validates
all maintained commit snapshots and final exact index, checks real stage ancestry,
spec-before-code/no-first-code ordering, full withdrawal sets and unchanged
withdrawn explanations/parents/sources. It checks semantic/edge/source changes
and executes six/seven/twenty model tests from isolated exports. Both redirects
retain 13/17 and 9/16 withdrawn live nodes; final graph is 22 live/22 withdrawn.
No original-history fingerprint bookkeeping, old reader fixtures or schema
migration tests remain. Application v1 JSON preview/conversion remains distinct.

Additional disposable Gantt Git tests check staged corruption hidden by repaired
worktrees, full-ID reparenting/renames, removed/added edges, impact and linked-source
ancestry. Root tests validate only present graph/context/manual-edit consistency;
old root schemes need not work. Current commit index checks still validate both
working graphs, as transaction hygiene rather than historical compatibility.

Local Windows evidence: full Python 100-test suite, current receipt/full-history
verifier, all three stage model suites, final 20 app tests and installed Chromium
Gantt smoke passed. The latter covers forecast/baseline, native caret/drafts,
cycle/deletion safety, literal text, downloads/uploads, conversion preview and
protected/denied storage. Complete VS Code and Electron real-host suites pass on
44-node working/45-node display Gantt fixtures, preserving all geometry/camera/
hover/paint and watcher assertions. VS Code additionally passes new equals-file
association, native dirty/save/undo/redo, raw-edit repair, split synchronization,
independent cameras and CRLF/Unicode saves. Electron passes sandbox/network,
actual UI save, retained stale-draft reload and current-schema revision switching.
Initial rekeyed-self-graph assertion failures are retained in the fixture choice.
Remote CI and non-Windows host runs are not claimed. This is bounded evidence,
not production/security/accessibility/performance certification or review proof.

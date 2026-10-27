# Current-directory authoring and first-run experience

This slice implements the owner's explicit onboarding/interface corrections.

## Contracts and choices

- Product text/chrome uses **specspec**. Distribution names are **specspec**,
  **specspec-vscode** and **specspec-desktop**. Portable desktop directories,
  executable and archives use `specspec-desktop`. Supplied original artwork and
  imported asset bytes remain exact; their original SVG provenance titles and
  archival owner input are preserved rather than falsifying those artifacts.
- `init` requires working Git. It reuses a containing Git working tree, including
  linked worktrees, or runs `git init` in the selected directory. This avoids
  accidentally nesting repositories inside an existing monorepo. It stages or
  commits nothing and configures neither identity nor hooks. A checkout-local
  exclusion protects runtime state without editing project ignore rules.
- `AGENTS.md` is created or concatenated with the packaged template. Existing bytes
  remain the exact prefix, with a paragraph separator when needed. Unsafe file/
  directory/symlink targets are rejected. Amended originals share exact-byte
  journaling/recovery with the manifesto; Git metadata is outside graph rollback.
- Direct nodes remain `.specspec/<id>.md`. The reserved `.specspec/local/` subtree
  holds locks, journals, spotlights, caches and retained diagnostics. Current,
  staged and historical node inventories exclude it. Other unsafe/noncanonical
  entries remain errors. Runtime notifications do not trigger canonical refreshes;
  spotlight watches follow each real directory boundary independently.
- Messages are literal. Without messages, init/add/update read bounded UTF-8 stdin;
  shell redirection supplies a file. Replacements consume no stdin. Empty stdin
  with metadata changes preserves body text, and interactive metadata-only updates
  do not wait for input. A nonempty stream has one unambiguous step. Managed UI
  empty bodies are rejected rather than silently retaining old text. Existing
  newline, size, original-byte, consent and native-document contracts remain.
- Every help body is 50–70% of its prior word count. Hidden project/structured-output
  switches never appear in help, including private command help. Ordinary queries
  and agent recipes omit internal version headers. Raw evidence and incompatible
  schema/protocol diagnostics retain their facts; no old readers are added.

## Shared startup and compatibility

Trusted hosts immediately probe the configured CLI using a bounded shell-free,
project-independent private handshake. The handshake reads no graph or stdin and
checks required stdin-body, project-init and nested-local-state capabilities.
Simply running `--version` would be insufficient: an older CLI with the same
protocol could accept update metadata while ignoring a new stdin body. Missing
capabilities therefore block before any graph operation rather than silently
losing a managed form edit. This adds no public version-selection controls.

A missing executable/module shows a prominent install-and-retry screen. Other
failures keep their actual diagnostics; they never masquerade as an empty project.
After prerequisites pass, an authorized absent/empty/local-only specification
folder offers a centered manifesto form and **Initialize specspec** button.
Initialization is explicit, scoped to the trusted host project, serialized, guarded
against dirty native documents and followed by fresh reads. Broken existing files,
unsafe paths and interrupted state are repair cases. Unknown mutation outcomes
are not replayed. Native VS Code forms retain native Save/undo ownership.

Electron removes the Project/Edit/View menu completely. Project selection remains
in the visible button and explicit Ctrl/Command+O handler; graph actions remain in
the shared toolbar. The old DevTools entry used Electron's native role, separate
from shared graph/session wiring. The sandbox, navigation/request allowlist and
permission policy remain unchanged. Menu removal is not presented as a proven
root-cause diagnosis of that old entry; broad graph/keyboard/source/persistence
regressions assess possible wider effects without weakening those protections.

## Maintained history and verification

The independent Gantt corpus is re-executed with current tools, lowercase prose,
current guides, real receipts and refreshed source anchors/ledgers/refs/bundle.
It preserves identities, topology, redirects, chronology and runnable behavior;
existing manual clones and previous bundles stay preserved. Node fields and the
machine envelope remain unchanged; this is not a node-schema migration.

Focused Python, shared DOM/session/transport, VS Code adapter and Electron security
checks cover the revised contracts, including absent/incompatible CLI, explicit
initialization, recovery, non-Git reads, SHA-256 repositories and local-state
exclusion. Non-Git tests deliberately remove only their disposable init-created
repository rather than pretending initialization leaves Git absent.

### Executed qualification

- Ubuntu/WSL2 on ext4: **1093 Python tests passed, zero skipped**. Windows: **1092
  passed**, with the POSIX permission case executed unchanged on Linux. JUnit case
  identities match across platforms; there are no unexecuted cases in the suite.
- Shared UI / VS Code / Electron unit suites: **267 / 53 / 11 passed**. Ruff and
  formatting pass. All 18 help bodies measure **64.7–70.0%** of their prior lengths.
- Fresh wheel and sdist installations in isolated uv-tool directories pass
  `specspec init -m "Test"`, Git setup, appended instructions, automatic stdin,
  metadata-only preservation, replacements, removed-flag rejection, hidden help,
  exact raw reads and newline checks. Imports come from installed site-packages.
- Both complete **installed Windows artifact-host suites pass**. New probes exercise
  missing-CLI guidance, retry, centered explicit initialization, Git and guide append;
  Electron checks missing CLI before project selection. Existing graph, source,
  keyboard, watcher, Git/deletion, spotlight/reload and native-document assertions
  remain. No production deadlines or save restrictions are loosened.
- All packages rebuild and inspection passes with the requested product names and
  new startup runtime. Current compiled/runtime bytes match installed artifact
  contents; Electron's intentionally stripped developer metadata is compared as
  runtime metadata rather than falsely requiring byte-identical package.json.
- The independent Gantt history verifies **22 nodes, 22 historical deletions, 123
  actual operations and all three runnable stages**. Every retained ref validates.
- Preparation used a **temporary review index** to validate exact staged graph/source
  bytes for **235 project / 22 example nodes**, with zero errors/warnings, leaving
  the real index untouched. The owner's subsequent explicit commit request authorizes
  staging the complete coherent change. Both checks are repeated against that actual
  index before commit, and the committed tree must match its validated tree.
  The tracked example is not its own Git workspace: its two changed verifier/HTML
  anchors require the incoming source tree. Staging retains those actual blobs;
  commit retains them in history. Independent bundled revisions also validate them,
  without weakening source-retention checks.

### Failures investigated

Changing init to establish Git required non-Git tests to deliberately remove their
own disposable repository. This also prevented a SHA-256 test from incorrectly
skipping after trying to reinitialize an already SHA-1 fixture. The oversized-input
regression uses a short parameter ID so pytest's environment does not itself exceed
OS argument limits before the actual input assertion. An initial full Linux run's
outdated contracts, then a test helper's missing stdin parameter and pending corpus
reconstruction, were corrected and the entire suite rerun.

Installed VS Code qualification exposed Windows drive-letter casing in the new
project-scope test selector, remaining obsolete body flags in existing fixture
mutations, and a keyboard probe pressing Save during its explicitly disabled
provisional phase. The selector now matches host filesystem semantics; a regression
scans adapter/fixture calls for obsolete flags. Keyboard probes wait for the
established enabled Save state, send one shortcut, and still assert exact persisted
bytes. Failed profiles/logs remain retained. Successful complete reruns follow the
corrections, not relaxed budgets or reclassification of failures.

Windows artifact-host execution and Ubuntu/WSL Python execution are separate scopes;
neither implies Linux graphical-host, macOS or remote execution qualification.
Diagnostic scripts, failed runs, original bytes, history backups and final reports
remain under `.specspec/local/owner-experience/`. Prior local diagnostics and
screenshots were moved intact. Preparation performed no owner installation, real
staging, commit, push, hook replacement or publication. The owner's later explicit
commit request authorizes the reviewed graph/code/docs/history/test slice, with
exact-index checks; it does not authorize pushing, publication or owner installs.

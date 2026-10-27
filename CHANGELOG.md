# Changelog

## 0.0.1 — initial PyPI CLI release

specspec connects intentions, separately revisable choices and implementation in a
local Git-versioned Markdown graph. This is an early release with evolving
interfaces and bounded verification, not a production/correctness guarantee.

### Install and distribute

- Install the CLI from [PyPI](https://pypi.org/project/specspec/) with
  `uv tool install specspec` or `pipx install specspec`. No checkout or Node is
  needed for the CLI. Current user/agent guides and both UIs recommend this path.
- All maintained Python/runtime/npm workspace/product versions are `0.0.1`.
  Internal schema/protocol and third-party dependency versions remain separate.
- An explicitly dispatched GitHub Trusted Publishing workflow verifies/builds/smokes
  the Python wheel and source distribution, then publishes them through environment
  `pypi` with short-lived OIDC identity and attestations. Local builds and ordinary
  pushes do not upload. [Release workflow](docs/releasing.md)
- VS Code remains a locally built/installed VSIX; desktop remains a portable,
  unsigned Windows/Linux app. They use the separately installed CLI and Git.
  Marketplace/npm publication, installers and auto-updates are not included.

Earlier development-only packages used `0.1.0`; this is the first public `0.0.1`,
not a promise that ordinary numerical upgrades will downgrade those local builds.
See [replacement/upgrade instructions](docs/install.md#upgrade-and-uninstall).

### Included behavior

- Seven everyday CLI verbs, concise task-oriented help, complete ancestor readings,
  Git-aware diffs and tracked source explanations. Integration controls and internal
  version headers stay out of ordinary help/readings.
- Literal repeatable messages, automatic bounded UTF-8 stdin without messages,
  newline/Markdown-prose-tolerant selected-passage replacements, and composed
  add/update/delete transactions with complete preflight and local aliases.
- Grouped Added/Modified/Deleted/Unchanged receipts with full unpadded IDs. Logical
  LF/CRLF/CR equivalence preserves meaningful text, blank lines and final-newline
  evidence. Complete managed/native-planned documents append a terminator only when
  missing; Git settings, attributes and raw-editor saves remain untouched.
- Explicit initialization requires Git, reuses a containing working tree or creates
  one, and creates/appends packaged `AGENTS.md` after exact original bytes. Node/guide
  journaling and recovery protect external edits; Git metadata remains Git-owned.
- Direct `.specspec/<id>.md` nodes and a reserved ignored `.specspec/local/` runtime
  subtree. Canonical inventories and watchers exclude that subtree.
- Shared graph UI with blocking compatible-CLI checks and centered explicit project
  initialization. Electron has no menu bar; its project picker/shortcut remain.
- Native VS Code Save/undo/dirty ownership; managed project/desktop byte-checked
  writes, exact selected deletion, invalid-graph repair, source uncertainty,
  spotlights, watchers and current/historical comparisons.
- One private npm workspace/lock, offline UI assets/license notices, inspected local
  artifacts, selected Spectrum flow branding and independent maintained Gantt history.

### Workspace and qualification boundaries

Canonical storage is `.specspec/`, not development-only `_specspec/`; keep IDs and
finish/recover old writes before changing paths/tools. Preserve recovery records,
experiments and native drafts. No compatibility reader or automatic history rewrite
is supplied. [Workspace upgrade](docs/install.md#upgrading-pre-release-workspaces)

Large graphs are not virtualized. Watchers are hints; recovery is not universal
Undo or guaranteed power-loss durability. No bundled Python/Git, hosted service or
built-in coding agent is included. Target platforms and actual executed qualification
remain separate. [Current release evidence](docs/investigations/pypi-0.0.1.md),
[earlier preparation](docs/investigations/release-0.1.md) and
[onboarding evidence](docs/investigations/owner-experience.md) retain their run scope.
Passing tests and source mappings are evidence, not semantic proof.

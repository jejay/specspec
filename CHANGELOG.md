# Changelog

## Unreleased

- Compare node text independently of LF/CRLF/CR encoding, without changing any Git
  configuration or attributes. Existing-document writes/native plans retain local
  newline style; new nodes use LF. Normal diffs omit encoding-only changes and
  newline counters; raw reads and physical transaction/recovery guards remain exact.

- Group mutation feedback by Added/Modified/Deleted/Unchanged with unpadded,
  comma-separated full node IDs. Init reports Added; previews use Would add/modify/
  delete. Classification compares logical text within the transaction, independently
  of Git status. Preserve diagnostics, explicit aliases and API-7 JSON records.

## 0.1.0 — initial release preparation

SpecSpec connects intentions, separately revisable choices and implementation in a
local Git-versioned Markdown graph. This is an early release, with evolving
interfaces and bounded verification rather than production/correctness claims.

### Included

- A globally installed, isolated Python CLI with seven everyday commands, detailed
  task-oriented help, complete ancestor readings, Git-aware diffs and source links.
- Repeatable literal messages and selected-passage replacements with default
  line-ending/Markdown prose-wrap tolerance; composed add/update/delete transactions.
- A locally built/installed VSIX for ordinary VS Code, retaining native document
  Save/undo/dirty ownership, raw Markdown and independent graph views.
- A standalone sandboxed Windows/Linux Electron editor and portable packaging,
  sharing the renderer/session/backend instead of a separate mutation engine.
- Root npm workspace commands/lock, Python wheels/sdist, artifact inspection and
  SHA-256 manifests, setup/contribution/release guides and the selected brand assets.
- A packaged `AGENTS.md` generated for newly initialized projects when absent,
  grounded in the supplied conceptual/CLI drafts and current working behavior.
- Exact selected deletion, visible invalid intermediates, explicit repair/recovery,
  bounded source uncertainty and owner-controlled Git operations.
- An independent maintained Gantt history with three runnable stages and two
  substantial redirects, reconstructed throughout for the current directory scheme.

### Pre-release directory change

Canonical nodes now live in **`.specspec/`** rather than `_specspec/`. Node IDs,
ID-only filenames, node fields, format 7 and API 7 retain their contracts. There is
one current location, not a compatibility reader. See [upgrade instructions](docs/install.md#upgrading-pre-release-workspaces)
before changing an existing workspace. Old manual clones/experiments are preserved;
arbitrary product history is not rewritten automatically.

### Deliberate limits

No Marketplace submission or assumed PyPI publication, signed installers,
auto-updater, bundled Python/Git, hosted service or built-in agent connector.
Desktop currently targets Windows/Linux; CLI and VS Code also target macOS with
separate execution qualification. Large graphs are not virtualized. Watchers are
filesystem-dependent hints; transaction recovery is not universal Undo or guaranteed
power-loss durability. Source mappings and passing tests are evidence, not semantic
proof. [Executed qualification and evidence](docs/investigations/release-0.1.md)

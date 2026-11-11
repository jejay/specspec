# Changelog

## Unreleased

**Agent guide.** `specspec init` ships a shorter AGENTS.md (about 12 KB). It starts with
what the graph is for and a working routine, shows a small example graph, reads
spotlights as owner input and states which commits a planning request authorizes: the
owner's pending specification edits, then the agent's result. A request to build includes
that planning, and every other commit follows the project's own rules. The agent leaves a
spotlight on the nodes it discusses, so the owner can open them in a graph editor. Three
worked examples show how a sentence from the owner becomes an outcome and a choice beneath
it. The guide keeps a list of limits in one node and names what stays out of the graph,
such as an order of work. When the owner has edited nodes by hand, the agent first tells
them what it would split, move or reword; what the owner does not accept stays as they
wrote it. Node text leaves out the time before the product and what the product is not.

**CLI fixes**
- A malformed node (deep nesting, oversized numbers, impossible dates) gets a FORMAT
  diagnostic of its own; the other nodes still load and raw reads still work.
- Unexpected errors produce a structured INTERNAL diagnostic instead of a traceback, and
  `api --stream` keeps serving after one.
- `diff` and the editors' comparison work with thousands of source references on Windows.
- `check --sources` accepts unchanged files of any length, reads only the referenced
  paths in large repositories and reports Git read failures as diagnostics.
- Source line numbers match editors, `grep` and Git for files with form feeds or other
  Unicode line separators.
- A second writer can no longer remove another writer's recovery journal.
- Git runs with fsmonitor, signature display and prompts turned off at every call site.
- `check --staged` ignores `git add -N` placeholders.

**Editor fixes**
- The CLI runs from a neutral directory with Python's safe import path, so a project's
  own Python files are never imported.
- Saving a new node twice in quick succession creates one node.
- Unsaved-change prompts work in VS Code, as a keyboard-accessible bar in the panel.
- The delete button reads "Delete node", matching what it does.
- Focus stays on the selected card across refreshes, and Tab follows the layout.
- Highlights and the manifesto outline are readable on light themes.
- Startup recovers from a slow webview, and a missing `--project` path shows a Retry
  screen.
- Several desktop windows keep each other's saved drafts.

**Documentation.** The README explains both spectra with figures. The editor guide is
the extension's README. Design notes and evidence moved into the specification graph
and commit messages.

## 0.0.1 — first public release

The CLI is on PyPI (`uv tool install specspec` or `pipx install specspec`); the VS Code
extension and the desktop app are built locally from this repository.

- Seven everyday commands with task-oriented `--help`: init, query, add, update, delete,
  check and diff.
- Node text from literal `-m` paragraphs or standard input; `update --replace` edits
  single passages; add, update and delete combine into one recoverable invocation.
- `query --with-ancestors` reads a node with everything that justifies it; distance and
  influence options select parts of large graphs.
- Implementation nodes link whole files or line ranges anchored to Git objects, and
  `check --sources` follows them through edits.
- Deleting a node removes exactly its file; descendants keep their references for
  deliberate repair.
- `init` sets up Git and adds the agent guide to AGENTS.md.
- One graph canvas in VS Code and in a Windows/Linux desktop app, with native node
  editing, revision comparisons and spotlights.

Development builds before 0.0.1 used `_specspec/` and the version 0.1.0. Rename the
folder to `.specspec/` after finishing or recovering interrupted writes, and replace
such a build with `uv tool install --force specspec`.

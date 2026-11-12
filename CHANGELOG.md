# Changelog

## 0.1.0 — first public release

The first release announced for feedback. The CLI is on PyPI
(`uv tool install specspec` or `pipx install specspec`); the VS Code extension and the
desktop app for Windows and Linux are downloads on the GitHub release. The changes below
are relative to 0.0.1, which was on PyPI without an announcement.

**Upgrading.** `specspec guide` brings a project's AGENTS.md to the guide of the
installed release: it finds the guide an earlier release added by exact match and
replaces it, and every other byte stays. A guide edited by hand is left alone with an
explanation. `init` adds the guide once and replaces an earlier release's guide in place.

**Editors.** Each version tag attaches the VSIX and the portable desktop archives to its
GitHub release, so the editors no longer need a build from source. The extension's
display name is specspec.

**Agent guide.** `specspec init` ships a shorter AGENTS.md (about 14 KB). It starts with
what the graph is for and a working routine, shows a small example graph and reads
spotlights as owner input. The agent leaves a spotlight on the nodes it discusses, so the
owner can open them in a graph editor. The guide keeps a list of limits in one node and
names what stays out of the graph, such as an order of work. Node text leaves out the time
before the product and what the product is not.

Intention and conclusion are the two ends of a link. Every node except the manifesto is a
conclusion from its parents and an intention for its children, and a conclusion is one
valid conclusion that another can replace at any depth. With anything the owner says, the
agent first tells intention from conclusion and finds out what the owner holds as fixed;
it asks when it cannot tell. It holds every conclusion against its intention, also a
statement right beneath the manifesto that makes no sense for the product, and points out
a conclusion in a manifesto's wording. Three worked examples show how a sentence from the
owner becomes an intention and a conclusion beneath it, and the agent's summary names the
intentions it read into the owner's words.

The guide names two kinds of commits. `Owner specspec changes:` holds the owner's hand
edits exactly as they wrote them; the agent makes this commit before it questions
anything. `Agent specspec changes:` holds the agent's planning, apart from implementation,
and seals the graph beneath it: the agent changes older nodes when a request needs it or
the owner asks for a review, and makes no remarks about their structure otherwise. A
request to build includes that planning, and every other commit follows the project's own
rules. What the owner changed by hand since the newest such commit, committed or not, gets
a structure review: the agent says what it would split, merge, move or reword, and what
the owner does not accept stays as they wrote it. A discussion before any planning closes
with guiding questions and the agent's own tentative answers.

**CLI fixes**
- Commands that need node text stop with a hint when nothing is piped in, instead of
  waiting. A UTF-8 byte-order mark on standard input is dropped, and other encodings
  are named in the error.
- A parent ID that does not exist is rejected before anything is written.
- Deleting uncommitted nodes asks only when both input and output are a terminal, and a
  refusal names `--yes`; on Windows an agent got a bare "Aborted!".
- Reads and writes wait a few seconds for another writer's lock and then name the cause;
  bounded queries report a lock or an interrupted edit as such.
- Staged files and the recovery journal reach the disk before any node changes, and
  `recover` removes a journal that cannot be read.
- Missing Git, an unknown revision and a conflicting strict source link each get a
  message that says what to do.
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

**Documentation.** The README explains both spectra with figures, and intention and
conclusion as a relation that holds at every depth. The editor guide is
the extension's README. Design notes and evidence moved into the specification graph
and commit messages.

## 0.0.1

Published to PyPI on 2026-10-27 without an announcement. The CLI installed with
`uv tool install specspec` or `pipx install specspec`; the VS Code extension and the
desktop app were built locally from this repository.

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

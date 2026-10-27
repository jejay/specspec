---
id: 83D9YWw=
type: requirement
parents:
- TAvql3w=
- 3fWBW_g=
---
# Materialize portable example artifacts in independent workspaces

Version the Gantt snapshot, complete bundle and stage/receipt ledger in specspec.
Git in the tracked folder resolves to this enclosing development repository.
A development checkout helper clones the bundle to an external standalone workspace,
default `~/Projects/specspec-examples/gantt`, or an explicit disposable destination.

Resolve paths, atomically reserve a new destination, refuse existing files/folders/
symlinks and destinations inside this development worktree, and retain partial
failed clones for inspection. Configure LF checkout. Preserve experiments in existing
clones. The tracked snapshot contains fixture files; external clones own independent
Git metadata, staging and history.

Serious Git/host/application integration and CI clone this entire bundle with its
stage tags/ancestry/index and add disposable worktree cues. Narrow synthetic graphs
remain useful for focused native/nested tests. CI needs portable tracked artifacts.
Validate every retained ref and snapshot/runtime consistency when refreshing them.

---
id: tvic3PQ=
type: requirement
parents:
- Bnr6yZY=
- YOPhqYc=
---
# Reconcile file and Git notifications while retaining drafts

Treat watcher events as reload hints. Coalesce events, serialize reads/writes, retry
transient reads a bounded number of times and compare loaded records directly to
skip unchanged redraws. VS Code uses filesystem watchers; Electron observes the
project parent and canonical directory and reattaches after directory recreation.
Report watcher errors. Explicit Refresh and optional configurable polling remain
available; polling defaults to 0/off and is disposed on switch/close.

Refresh clean forms. Dirty forms retain original records, text, caret and camera;
unrelated changes refresh context while preserving save eligibility. Same-node
changes require overwrite confirmation. Deleted drafts stay copyable and unsavable.
Graph-invalid reloads display actual current relationships and diagnostics while
permitting safe local edits. Unreadable targets retain raw repair access; unavailable
loads retain clearly marked last-usable context without enabling stale writes. Historical views retain their selected
revision. Rendering acknowledgements use sequence tokens and full visible membership.
Watchers are filesystem-dependent notification hints; byte-checked transactions
supply a separate persistence boundary.

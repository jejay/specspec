---
id: Bnr6yZY=
type: requirement
parents:
- ME4UXTA=
- PL1IogE=
---
# Permit manual Markdown changes and keep the UI synchronized

Remove graph fingerprints, managed_hash markers, and hash-based editing gates.
The CLI and visual editor remain the recommended ways to change the graph, but
manual Markdown changes are permitted: users are consenting adults, not subject
to provenance enforcement. Continue checking actual schema and graph consistency.

Synchronize both UIs with external Markdown changes through file watchers. Offer
configurable polling as an optional supplement, disabled by default; the default
should run through watchers alone. Preserve unsaved text, native caret and camera
state rather than silently overwriting drafts during synchronization. Report
invalid files without silently repairing them or presenting stale data as current.

Origin: the user's explicit manual-edit/fingerprint-removal and watcher/default-off
polling correction in this conversation. Mechanisms and schema versions are choices.

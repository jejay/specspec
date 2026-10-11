---
id: 5c2b23ba-7bbc-4458-b63e-808e58cd7059
type: requirement
parents:
- 003d697b-4104-4fdf-8e05-0db572c436d0
- 5563649e-f76e-4c59-8e1d-52f60be938ee
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

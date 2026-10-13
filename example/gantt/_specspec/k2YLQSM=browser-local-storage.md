---
id: k2YLQSM=
type: requirement
parents:
- WpnnQRQ=
- J3ggsWw=
---
# Use localStorage with an explicit failure boundary

Use browser localStorage for convenient valid-plan autosave. If unavailable, keep the app usable in memory and warn. Corrupt saved bytes are not silently overwritten; explicit reset is needed to replace them. This is browser-local, not synchronization or guaranteed durable backup. Origin: STORY.md, AI redirect-one conclusion.

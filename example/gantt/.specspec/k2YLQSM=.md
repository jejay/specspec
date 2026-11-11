---
id: k2YLQSM=
type: requirement
parents:
- WpnnQRQ=
- J3ggsWw=
---
# Autosave through localStorage with protected original bytes

The validated plan is saved in the browser's localStorage under a stable local origin.
When storage fails, the app keeps working in memory and shows that the plan is
session-only and how to export it. Saved bytes that cannot be read stay as they are
until the person resets them or replaces them through a previewed import. Browser
storage depends on the browser, the origin and its storage settings; the exported file
is the copy the person controls.

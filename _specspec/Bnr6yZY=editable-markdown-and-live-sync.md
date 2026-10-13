---
id: Bnr6yZY=
type: requirement
parents:
- ME4UXTA=
- PL1IogE=
---
# Synchronize permitted manual edits while preserving user input

Keep both UIs synchronized with external canonical Markdown changes through file
watchers. Offer explicit configurable polling as an optional supplement, initially
disabled. Retain unsaved text, caret and camera state during synchronization.

Report invalid saved files with actionable diagnostics and a clearly out-of-date
last valid view. Saving an externally changed edited node requires overwrite
confirmation; unrelated graph changes leave a draft usable. Canonical consistency
is determined by contents, with transaction guards based on original file bytes.

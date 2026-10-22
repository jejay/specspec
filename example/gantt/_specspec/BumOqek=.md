---
id: BumOqek=
type: requirement
parents:
- MKQSeG4=
- ewV6-hc=
- rrN-aHA=
---
# Define version-two workshop JSON and previewed conversion

A `version: 2` envelope has title/start/tasks and optional full baseline. Tasks have
id/title/duration/earliest/dependsOn. Normalize copied fields, validate both forecasts
and their common axis, and serialize saved data. Import preview accepts up to one
million characters; file input is bounded to one million bytes. Apply explicitly
replaces saved work/storage after confirmation; cancel retains both.

Convert valid version-one ranges to the count of contained weekdays, minimum one
workday; keep each old start as earliest, create empty prerequisite arrays and an
empty baseline, and use the earliest task start as project start (2026-04-06 for
an empty plan). Consume the v1 priority as conversion input and report its omission.
Warn that manual end becomes a duration-derived forecast and weekend-only ranges
advance to a workday. Keep stored v1 bytes protected pending preview/Apply/reset.

---
id: BumOqek=
type: requirement
parents:
- MKQSeG4=
- ewV6-hc=
- rrN-aHA=
---
# Define version-two workshop JSON and previewed conversion

A `version: 2` file holds title, start, tasks and an optional complete baseline. A task
has id, title, duration, earliest and dependsOn. Loading normalizes copies of the fields
and validates both forecasts and their common axis; saving serializes the saved plan.
The import preview accepts up to one million characters of pasted text and files of up
to one million bytes. Apply replaces the saved work and the browser storage after
confirmation; Cancel keeps both. A valid version-one range becomes a duration of the
weekdays it contains, at least one; the old start becomes the task's earliest date,
prerequisites and the baseline start empty, and the project starts at the earliest task
start, or on 2026-04-06 for an empty plan. The version-one priority is read and reported
as dropped. The preview warns that a hand-entered end becomes a forecast from the
duration and that a range lying on a weekend moves to a workday. Stored version-one
bytes stay protected until preview and Apply, or reset.

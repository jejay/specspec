---
id: XZk4rMA=
type: requirement
parents:
- GVd1MQw=
- D9uv83Q=
- YzpuAJs=
- L2aeTSg=
- J3ggsWw=
---
# Calculate bounded UTC weekday DAG forecasts iteratively

Dates are whole days in UTC, and tasks are processed iteratively in prerequisite order.
A task starts on the latest of the normalized project start, its own normalized earliest
date and the next weekday after each prerequisite's end; it ends duration minus one
workdays after its start. The result lists the tasks in saved order and leaves the input
unchanged. A plan is valid with up to 100 tasks, durations of 1 to 60 whole workdays,
real ISO dates from 2000 to 2100, unique task IDs of 1 to 40 letters, digits, `_` or
`-`, trimmed titles and names of 1 to 120 characters, and prerequisites that are
distinct existing tasks other than the task itself. A cyclic or invalid plan is
rejected. The earliest date may be null or empty. The current plan and the baseline
together fit an axis of at most 730 calendar days, counted inclusively over the
normalized starts and all forecast rows. The model is a small deterministic dependency
forecast.

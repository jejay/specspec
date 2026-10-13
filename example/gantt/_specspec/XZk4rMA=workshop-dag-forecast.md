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

Use whole UTC dates and iterative topological processing of all prerequisites.
Start is the maximum of normalized project start, normalized optional earliest and
next weekday after each predecessor end. End is duration-1 workdays after start.
Return rows in saved task order and preserve inputs.

Validate up to 100 tasks, durations 1–60 whole workdays, real ISO dates 2000–2100,
unique 1–40 character letter/number/_/- task IDs, trimmed title/names of 1–120
characters and distinct existing non-self prerequisites. Reject cyclic or invalid
candidates. Earliest may be null/empty. Current and baseline together fit an
inclusive axis of at most 730 calendar days; include normalized starts and all
forecast rows in its bounds. The model is a small deterministic dependency forecast.

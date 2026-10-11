---
id: fc2a2b2f-a7b0-4980-87d9-4f57101445a2
type: requirement
parents:
- 1647ecb7-4aa9-406e-a95a-d8e10f1a2d95
- 2accd6ea-e2a4-4f33-9bac-43245831939a
- 99297cc8-fbfc-473c-a6ce-3fece85d00ce
- 11b2353d-5dee-4830-8b70-98e0952df124
- 928060fa-c02d-46dd-b823-b002bcf41353
---
# Use iterative weekday finish-to-start forecasting

Use whole UTC days and deterministic topological traversal of all prerequisites. Start is the latest of normalized project start, normalized optional earliest date, and next workday after every predecessor finish. End is duration-1 workdays later. Reject cycles, missing/repeated/self links, invalid dates, excess tasks/durations, or a combined current/baseline chart horizon over 730 calendar days before applying a change. Maximum 100 tasks, duration 1-60 workdays, dates 2000-2100. These bounds keep a small DOM chart practical, not an optimal scheduler. No holidays or resource leveling. This is a NEW conclusion, not restoration/approval of the withdrawn portfolio scheduler. Origin: STORY.md, AI redirect-two conclusion.

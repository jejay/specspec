---
id: rrN-aHA=
type: requirement
parents:
- fcXPQQQ=
- 39Myh1I=
- XZk4rMA=
---
# Store an explicit deep baseline and compare on a common axis

On request the app stores a normalized copy of the complete saved plan, and later edits
leave that copy as it is. The current plan and the baseline are forecast independently
and drawn on the same bounded calendar axis: the current tasks in their order, followed
by tasks that exist only in the baseline. The text view gives start, end and the
difference of the finish dates in calendar days. A task found only in the baseline stays
visible as removed, a task found only in the current plan is marked Added, and a missing
baseline date leaves the comparison empty. Replacing and clearing the baseline are
explicit actions, and validation leaves both snapshots as they are.

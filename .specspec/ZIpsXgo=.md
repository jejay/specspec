---
id: ZIpsXgo=
type: requirement
parents:
- kPnORhs=
- EANel4I=
---
# Seal the graph beneath every agent planning commit

A commit titled `Agent specspec changes:` seals every node as it stands in that commit. The agent changes a sealed node where a request cannot be recorded well without the change, or when the owner asks for a review or a restructuring, and its summary names the sealed nodes it changed.

What the owner changed by hand after the newest such commit is open, whether the owner committed it, the agent committed it for them or it is still uncommitted. Open nodes get the structure review. A graph without such a commit is open as a whole.

The line is drawn leniently. How far a change for a request reaches into sealed nodes is the agent's judgment.

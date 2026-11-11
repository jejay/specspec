---
id: 3Kq9RNw=
type: implementation
parents:
- xQszOxI=
sources:
- path: STORY.md
- path: README.md
- path: history/WALKTHROUGH.md
- path: history/cli.jsonl
- path: history/revisions.json
- path: history/verify.py
  blob: 4c12e82dcef55b0ba9d7798856aaf601a6049ee6
  mode: expanding
  ranges:
  - - 1
    - 381
---
# Receipts, a stage ledger and a verifier for the recorded history

`history/cli.jsonl` holds the specspec commands that built this graph, with their actual
results. `history/revisions.json` names the planning commit and the code commit of every
stage and the receipts that end them. Planning commits come before the code they plan,
and the commit of each redirect says what was deleted and why; the deleted nodes stay
readable in the commits before it. `history/verify.py` checks every commit and tag of
this history: valid graphs in the current format, the exact staged state, the receipts
against the graphs, the order of planning and code, what each redirect removed, the
source links and the model tests of every stage. `STORY.md` tells the product briefs as
a fictional dialogue, and `README.md` and `history/WALKTHROUGH.md` explain how to open
and compare the stages.

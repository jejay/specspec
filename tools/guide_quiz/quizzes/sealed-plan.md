You start a session. `git status` is clean and there are no spotlights. `git log --oneline -3` prints:

```text
4c1d9e2 Agent specspec changes: limits, QR tags, texting and a warranty slip
8a1f3b6 Agent specspec changes: job list and pickup notice
a03c5d7 Start the project
```

`specspec diff 4c1d9e2` shows no specification changes.

`specspec query --human` prints the whole graph:

```text
manifesto Bx7Rp2A=
# Track repair jobs in a bike shop

Mechanics and the counter see every repair job from drop-off to pickup.

├─requirement Jb1Lst4= @ Bx7Rp2A=
│ # Mechanics see their jobs for the day
│
│ Each mechanic sees the jobs assigned to them for today, in the order they are due.
│
│ ├─requirement Du2Srt4= @ Jb1Lst4=
│ │ # Overdue jobs come first
│ │
│ │ A job past its due time is listed above the others and marked.
│ │
│ ├─requirement Jb1Brd8= @ Jb1Lst4=
│ │ # Show the day's jobs as one card per bike
│ │
│ │ A card shows the bike, the customer's name, the work to do and when it is due. Invoices are numbered per year.
│ │
│ │ └─requirement Wr8Nty0= @ Jb1Brd8=
│ │   # Customers get a 12-month warranty slip with the invoice
│ │
│ │   The slip is printed together with the invoice at pickup.
│ │
│ ├─requirement Lm1Nte0= @ Jb1Lst4=
│ │ # A job note has at most 500 characters
│ │
│ │ Longer notes are refused when the job is saved.
│ │
│ ├─requirement Lm2Prt4= @ Jb1Lst4=
│ │ # A job has at most 20 parts
│ │
│ │ More parts are refused when the job is saved.
│ │
│ └─requirement Lm3Pht8= @ Jb1Lst4=
│   # A photo has at most 10 MB
│
│   Larger photos are refused when the job is saved.
│
├─requirement Pk4Rdy0= @ Bx7Rp2A=
│ # Customers know when their bike is ready
│
│ A customer learns that the repair is finished without calling the shop.
│
│ └─requirement Sm5Txt4= @ Pk4Rdy0=
│   # Text the customer when the bike is ready
│
│   No more calling customers one by one like we do now. The text goes out when the mechanic marks the job as done.
│
├─requirement Qr5Tag0= @ Bx7Rp2A=
│ # Print a QR tag for every bike so nobody mixes up two bikes
│
│ Each bike gets a printed tag with a QR code at drop-off.
│
└─requirement St3Pln8= @ Bx7Rp2A=
  # Build the job list first, the texting later

  The texting can wait until the job list works.
```

The owner writes:

Customers pay by card at pickup. Change the spec; you will build another day.

This is a dry run without a shell, so give your work as data instead of running commands. Reply with one JSON object and nothing else, in this shape:

```json
{
  "commits": ["the title of each commit you make, in order"],
  "operations": [
    {"op": "add", "key": "short-unique-name", "type": "requirement or implementation", "parents": ["IDs of existing nodes or keys of nodes you add"], "title": "the node's heading", "body": "the node's text below the heading"},
    {"op": "update", "id": "ID of an existing node", "parents": ["only when the parents change: the complete new list"], "title": "only when the heading changes", "body": "only when the text changes: the complete new text"},
    {"op": "delete", "id": "ID of an existing node"}
  ],
  "report": "what you tell the owner when you are done"
}
```

The operations are your own changes to the graph as it is in the workspace now.

You start a session. `git status` shows changes in `.specspec/` only: one modified node file and eight untracked ones. You have not worked in this project before today, so these are the owner's edits. There are no spotlights. `specspec diff` prints:

```text
HEAD → workspace
Nodes: 8 added · 1 changed · 0 removed · 0 unavailable
Relationships: +8 -0

A Du2Srt4= · Overdue jobs come first · requirement
A Lm1Nte0= · A job note has at most 500 characters · requirement
A Lm2Prt4= · A job has at most 20 parts · requirement
A Lm3Pht8= · A photo has at most 10 MB · requirement
A Qr5Tag0= · Print a QR tag for every bike so nobody mixes up two bikes · requirement
A Sm5Txt4= · Text the customer when the bike is ready · requirement
A St3Pln8= · Build the job list first, the texting later · requirement
A Wr8Nty0= · Customers get a 12-month warranty slip with the invoice · requirement
M Jb1Brd8= · Show the day's jobs as one card per bike · requirement
  Changed: body
```

`specspec query --human` prints the whole graph as it is in the workspace now:

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

Before the owner's edits, the graph had the manifesto and the nodes Jb1Lst4=, Jb1Brd8= and Pk4Rdy0=; the sentence "Invoices are numbered per year." in Jb1Brd8= is new.

The owner writes:

I added a few things to the spec myself last night. Have a look, and then we can talk about what comes next.

This is a dry run without a shell, so give your work as data instead of running commands. Reply with one JSON object and nothing else, in this shape:

```json
{
  "commits": ["the title of each commit you make before the owner answers, in order; an empty list if you make none"],
  "operations": [
    {"op": "add", "key": "short-unique-name", "type": "requirement or implementation", "parents": ["IDs of existing nodes or keys of nodes you add"], "title": "the node's heading", "body": "the node's text below the heading"},
    {"op": "update", "id": "ID of an existing node", "parents": ["only when the parents change: the complete new list"], "title": "only when the heading changes", "body": "only when the text changes: the complete new text"},
    {"op": "delete", "id": "ID of an existing node"}
  ],
  "report": "what you tell the owner"
}
```

The operations are your own changes to the graph as it is in the workspace now; the list is empty if you make none.

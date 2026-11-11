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

The owner wrote:

I added a few things to the spec myself last night. Have a look, and then we can talk about what comes next.

You answered:

I read your edits against the rules for structure and wording. Nothing is changed yet. I would suggest six changes:

1. Qr5Tag0= names a way and its purpose in one node. I would make "No two bikes get mixed up" an outcome and put the QR tag beneath it as a choice.
2. Jb1Brd8= now also says "Invoices are numbered per year." That is a separate decision, so I would move it into a node of its own.
3. Sm5Txt4= refers to how you call customers today. I would reword it to say only what the product does.
4. St3Pln8= is an order of work. I would take it out of the graph and simply follow it.
5. Lm1Nte0=, Lm2Prt4= and Lm3Pht8= are three limits of one decision. I would merge them into one node.
6. Wr8Nty0= hangs under the card view, which is not its reason. I would move it under the manifesto.

Du2Srt4= is fine as it is. Tell me which of these you want; everything else stays as you wrote it.

The owner writes:

Do 1, 4 and 5. Leave 2, 3 and 6 exactly as I wrote them. Then change the spec; you will build another day.

You committed the owner's edits as they wrote them, under the title `Owner specspec changes: QR tags, limits, texting, a warranty slip and an order of work`. `git status` is clean.

This is a dry run without a shell: no command prints anything back to you, so the ID of a node you add stays unknown to you. Give the specspec commands that make your changes to the graph, as you would type them in a POSIX shell. Leave out reads, checks and Git commands. Reply with one JSON object and nothing else, in this shape:

```json
{
  "commands": ["one complete command line per entry, in the order you run them"],
  "report": "what you tell the owner when you are done"
}
```

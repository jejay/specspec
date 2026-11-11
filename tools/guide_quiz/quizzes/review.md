`git status` is clean, `specspec diff` shows no changes and there are no spotlights. `specspec query --human` prints the whole graph:

```text
manifesto Tb4Lq7A=
# Let neighbours borrow tools from a shared shed

Members reserve, collect and return the shed's tools without a volunteer keeping lists by hand.

├─requirement Ft9sKe2= @ Tb4Lq7A=
│ # Features
│
│ What the app offers to members.
│
│ ├─requirement Rs3vDy5= @ Ft9sKe2=
│ │ # Members reserve a tool for whole days
│ │
│ │ A member picks a tool and one or more days and knows at once whether the tool is theirs for those days.
│ │
│ │ ├─requirement Cl6ndr8= @ Rs3vDy5=
│ │ │ # Calendar
│ │ │
│ │ │ Each tool has a month calendar that marks its reserved days. A day is the shed's opening time, 8:00 to 20:00.
│ │ │
│ │ │ └─requirement Dm2gRp4= @ Cl6ndr8=
│ │ │   # Members report damage when they return a tool
│ │ │
│ │ │   The next member learns about a blunt blade or a missing part before they collect the tool.
│ │ │
│ │ ├─requirement Sq1Lte7= @ Rs3vDy5=
│ │ │ # Use SQLite
│ │ │
│ │ │ The volunteer who hosts the app insists on SQLite, because the shed's old laptop runs nothing else.
│ │ │
│ │ ├─requirement Hr5Day3= @ Rs3vDy5=
│ │ │ # Reserve by the day
│ │ │
│ │ │ Reservations are now per day instead of per hour, since the earlier hourly slots confused members.
│ │ │
│ │ └─implementation ImRs0v6= @ Rs3vDy5=
│ │   sources: app/reservations.py
│ │
│ │   # Reservation storage
│ │
│ │   `reservations.py` keeps reservations in one JSON file per tool rather than in the database, which was quicker to write.
│ │
│ └─requirement Rm8ndE1= @ Ft9sKe2=
│   # Send an e-mail the evening before a tool is due, so that tools come back on time
│
│   Members who forget are the main reason why a tool is missing when the next member comes.
│
├─requirement St4pOn9= @ Tb4Lq7A=
│ # Step 1: set up the database, step 2: reservations, step 3: reminders
│
│ Build in this order. Reminders can wait until members use the reservations.
│
└─requirement Bk7Tim2= @ Tb4Lq7A=
  # Tools come back on time

  The next member finds the tool they reserved.

  └─requirement Tm3Rtn5= @ Bk7Tim2=
    # Ensure timely returns

    Tools should be returned on time.

    ├─requirement Fe6Lat8= @ Tm3Rtn5=
    │ # Charge 1 € for each day a tool is late
    │
    │ The fee is added to the member's account when the tool is returned. A day is the shed's opening time, 8:00 to 20:00.
    │
    └─requirement Op9Blk0= @ Tm3Rtn5=
      # Option B: block members who have an overdue tool

      An alternative to the late fee. To be decided.
```

The owner writes:

Before we go on, please review the structure of this graph. Tell me what you would change and why. Leave the graph as it is for now.

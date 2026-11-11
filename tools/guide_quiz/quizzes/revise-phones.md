`git status` is clean, `specspec diff` shows no changes and there are no spotlights. `specspec query --human` prints the whole graph:

```text
manifesto Kq3x9bA=
# Run a physiotherapy practice's appointments

One place where the front desk and four therapists book, see and change appointments, and patients are reminded of them.

├─requirement B00kMv1= @ Kq3x9bA=
│ # The front desk books, moves and cancels appointments
│
│ One person at the front desk handles all changes. Moving an appointment takes a few seconds.
│
│ └─implementation ImB00k2= @ B00kMv1=
│   sources: web/booking.js
│
│   # Booking form and drag-to-move
│
│   `booking.js` holds the booking form and moves an appointment when its card is dragged to another time.
│
├─requirement EuData9= @ Kq3x9bA=
│ # Patient data stays on servers in the EU
│
│ No patient data is stored or processed outside the EU, including by services the app calls.
│
│ └─↪ SmsDay6= ↓
├─requirement Rm1ndR3= @ Kq3x9bA=
│ # Patients are reminded of their appointment in time
│
│ A patient hears from the practice early enough to rearrange their day or to cancel.
│
│ └─requirement SmsDay6= @ EuData9=, Rm1ndR3=
│   # Send the reminder as a text message the day before
│
│   Texts go out at 18:00 on the day before the appointment, through an SMS gateway hosted in Frankfurt. The front desk signs in with the practice's Microsoft accounts.
│
│   └─implementation ImSms77= @ SmsDay6=
│     sources: jobs/reminders.py
│
│     # Evening reminder job
│
│     `reminders.py` runs at 18:00, selects tomorrow's appointments and sends one text per patient through the gateway's HTTP API.
│
└─requirement Wk7fTq0= @ Kq3x9bA=
  # Everyone sees who is treated when and by whom

  Front desk and therapists see the practice's appointments without opening single ones.

  └─requirement Gr1dCc4= @ Wk7fTq0=
    # Show the week as a grid with one column per therapist

    A week view in the style of a desktop calendar: the days side by side, and within each day one column per therapist.

    ├─requirement C0lrTy2= @ Gr1dCc4=
    │ # Colour each appointment by treatment type
    │
    │ Manual therapy, massage and training each have their own colour, so the mix of a day shows without reading.
    │
    │ └─↪ ImGr1d5= ↓
    └─requirement Sl0tRw8= @ Gr1dCc4=
      # Rows are 15-minute slots from 7:00 to 20:00

      Every appointment starts and ends on a slot boundary.

      └─implementation ImGr1d5= @ C0lrTy2=, Sl0tRw8=
        sources: web/week-grid.js

        # Week grid rendering

        `week-grid.js` draws the grid, places appointments on their slots and colours them by treatment type.
```

The owner writes:

Three changes.

1. The week grid is useless on the therapists' phones. Show a list for one day at a time instead. The colours by treatment type should stay.
2. Patients should be able to answer the reminder text with YES, so that we know who is coming.
3. Some patients have no mobile phone. They should get the reminder by e-mail.

Please change the spec. You will change the code another day.

This is a dry run without a shell, so give your changes as data instead of running commands. Reply with one JSON object and nothing else, in this shape:

```json
{
  "operations": [
    {"op": "add", "key": "short-unique-name", "type": "requirement or implementation", "parents": ["IDs of existing nodes or keys of nodes you add"], "title": "the node's heading", "body": "the node's text below the heading"},
    {"op": "update", "id": "ID of an existing node", "parents": ["only when the parents change: the complete new list"], "title": "only when the heading changes", "body": "only when the text changes: the complete new text"},
    {"op": "delete", "id": "ID of an existing node"}
  ],
  "report": "what you tell the owner when you are done"
}
```

The project was initialized a minute ago. `specspec init` created this AGENTS.md and the manifesto below. There are no other nodes and there is no code yet.

```text
manifesto Kq3x9bA=
# Run a physiotherapy practice's appointments

One place where the front desk and four therapists book, see and change appointments, and patients are reminded of them.
```

The owner writes:

I run a physiotherapy practice: four therapists and one person at the front desk. I want a small web app for our appointments. What I have in mind:

- The front desk books, moves and cancels appointments. Moving one should take seconds. Today it is phone tag and a paper calendar.
- Everyone sees the week at a glance, per therapist. I picture a week grid like in Outlook, with the therapists as columns.
- Patients get a text message the day before, so fewer of them forget their appointment.
- It has to run on the PostgreSQL server our IT contractor already hosts for us. He supports nothing else.
- For the text messages maybe use Twilio, or whatever you find best.
- Patient data must not leave the EU.
- A therapist or a room can only have one appointment at a time.
- Appointments last 20, 30, 45 or 60 minutes, between 7:00 and 20:00, Monday to Saturday.
- Therapists want their week on paper for home visits, and in the calendar app on their phone.
- First set up the project with CI, then the booking part. The reminders can come last.
- What the reminder says exactly is up to you.

Please draw the graph. You will build the app another day.

This is a dry run without a shell, so give the graph as data instead of running commands. Reply with one JSON object and nothing else, in this shape:

```json
{
  "nodes": [
    {
      "key": "short-unique-name",
      "type": "requirement or implementation",
      "parents": ["manifesto, or keys of other nodes"],
      "title": "the node's heading",
      "body": "the node's text below the heading"
    }
  ],
  "report": "what you tell the owner when you are done"
}
```

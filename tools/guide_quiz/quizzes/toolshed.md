The project was initialized a minute ago. `specspec init` created this AGENTS.md and the manifesto below. There are no other nodes and there is no code yet.

```text
manifesto Tl8bRw4=
# A web app with a calendar view for the neighbourhood tool library

Neighbours borrow tools from the shed and bring them back on time.
```

The owner writes:

I look after the tool shed of our neighbourhood association: about 120 tools, 60 member households and one shed with a door code. I want a small app for lending. What I have in mind:

- A member scans the QR code on a tool with their phone to borrow it, and scans it again to bring it back.
- Two days before a tool is due, the member gets an e-mail.
- A sheet on the shed door lists the tools that are out and when each is due back. I print it every Monday.
- Everything runs on the small server in the association's office. The board pays for nothing else.
- I would build it with Vue.
- A household has at most 3 tools at a time, a loan lasts at most 14 days, and a tool can be reserved up to 30 days ahead.
- When a tool comes back broken, the member writes what happened and I get a notice, so that I can take it out of lending.
- The chainsaw and the wood chipper go only to members who did the safety briefing.
- Start with borrowing and returning, then the rest.
- What the e-mail says is up to you.

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

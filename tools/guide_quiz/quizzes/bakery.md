The project was initialized a minute ago. `specspec init` created this AGENTS.md and the manifesto below. There are no other nodes and there is no code yet.

```text
manifesto Bk2rPm8=
# Take pre-orders for a neighbourhood bakery

Customers order bread and cakes ahead and pick them up in the shop.
```

The owner writes:

I run a bakery with two bakers and one shop assistant. I want a small web app for pre-orders. What I have in mind:

- Customers order ahead for a pickup day on their phone, without creating an account. Right now they call or leave paper notes, and half of it gets lost.
- The bakers get a big board on the screen in the bakehouse with tomorrow's orders, so they know what to bake first.
- Customers get an e-mail when their order is ready, so nobody waits in the shop for nothing.
- It has to run on the mini PC under the counter. The landlord allows no other hardware, and I will not pay for hosting.
- For sending the e-mails maybe use our web host's mailbox, or whatever you find best.
- Everything a customer sees is in German and in Turkish.
- An order can be handed out only once. The assistant marks it as picked up.
- An order has at most 20 items, is placed by 18:00 on the day before pickup, and is picked up between 6:30 and 12:30.
- Customers want a printed slip in the bag, and something on their phone that they can show at the counter.
- Start with the order form. The board can come later, the e-mails last.
- How the e-mail is worded is up to you.

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

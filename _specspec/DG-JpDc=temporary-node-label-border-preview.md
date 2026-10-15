---
id: DG-JpDc=
type: requirement
parents:
- t8RQMdE=
- PL1IogE=
---
# Exchange owner and agent messages as local colored node spotlights

An owner can send highlighted node sets and a message to an external agent, and
can ask an external coding agent which nodes express an idea. The agent
uses spotlight add with color names, full node IDs and one spotlight message as
command-line arguments. Each spotlight contains one message and one or more colored
node sets. Both visual hosts offer retained spotlights through the Spotlights
button's dropdown. Selecting a spotlight highlights all its colored sets together
and frames the matching nodes in the surrounding graph context.

Manual and spotlight-applied highlights form one editable per-view set. Owners
can save that set with a message as a new spotlight for an external agent to read.

A new spotlight attracts attention through the toolbar's new-count badge while
preserving the owner's current editing and navigation. Spotlights remain local,
outside Git, across sessions and branch changes until explicitly flushed. Each
addition publishes one immutable record. Members retain full node IDs and exact
Git-blob content addresses; resolution preserves submitted membership and message.

---
id: rQTg56g=
type: requirement
parents:
- 7tMgRa8=
- P2i_png=
---
# Take the node IDs and one message of a spotlight as plain arguments, with options for base and target

`spotlight add NODE_ID... MESSAGE` records one message about nodes of a comparison, which `--base REV` and `--target REV|workspace` select. Without them the comparison is the live HEAD against the working files, and a Git ref that is named resolves to an immutable commit. The command reads full node IDs in their canonical form from the front of its arguments, including IDs that begin with a dash, and joins the remaining words into the message. It requires at least one ID, each ID once, and a message that is not blank and has at most 500 characters. A word for a color is ordinary text of the message and has no structural role. Before a spotlight is published, each ID is validated against what the comparison knows: the nodes parsed from the target and from the base, the IDs that nodes declare as parents and that are missing, and the names of the node files in the inventory. An ID whose file cannot be read stays an unavailable member and adds no node to the graph. The arguments are the whole input of the command.

`spotlight show` takes an optional full spotlight ID and reports for each record its own comparison, its message, the status of each member as derived from that comparison or its unavailability, the title of each member, and warnings about the working files and the context. `--json` gives the same records with structured statuses. `spotlight flush --yes` clears the local store explicitly. The creation operation of the application protocol takes one message and a list of node IDs, without colors, together with the current comparison of the editor and the text of its open documents, both of which it trusts.

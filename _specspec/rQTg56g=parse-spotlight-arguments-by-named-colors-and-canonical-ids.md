---
id: rQTg56g=
type: requirement
parents:
- 7tMgRa8=
- P2i_png=
---
# Parse spotlight arguments by named colors and canonical IDs

Expose spotlight add [[color-name] [node-id]+]+ MESSAGE. Recognize red, blue,
green, purple, turquoise and yellow as color markers and canonical padded
Base64url IDs as members. A marker applies to following IDs until the next marker;
IDs before the first marker use purple. Require at least one ID per marked set
and a nonblank message of at most 500 characters. The first argument that is
neither a named color nor a canonical ID begins the message; join remaining
arguments with spaces so quoted and ordinary multiword messages work naturally.
Shell quoting preserves a message as one argument; standalone colors and IDs in
the leading prefix remain structural tokens. Support dash-leading canonical IDs.
Reject repeated members across the new spotlight so each node has one color.
Validate every node before atomic publication. Add supports --ref for capture
and --json for output. Show and confirmed flush keep their existing read/lifetime
semantics. Commands accept arguments directly rather than file/JSON input.

One stored shot represents the whole spotlight. Ordered internal color groups
repeat its single message, reusing the existing checkout-local storage format. The
dropdown applies all exact matching groups to the editable highlight set. For
retained records with overlapping groups, later groups determine the ring color.

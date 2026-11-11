---
id: DG-JpDc=
type: requirement
parents:
- t8RQMdE=
- PL1IogE=
---
# Exchange owner and agent messages as local node spotlights

An owner and an external coding agent exchange spotlights: one message together with the full IDs of selected nodes. Both graph editors offer the stored messages under Spotlights. Selecting one switches to the comparison of revisions that belongs to it, highlights those of its nodes that are available, all in one shared ink, and frames them in their graph context.

The highlights that the owner sets by hand and those that a spotlight applied form one editable set per view. The owner can save this set with a message as a new spotlight, which is immutable, for an external agent to read. An arriving spotlight draws attention through a count of new ones and leaves editing and navigation undisturbed. Spotlights stay local and outside Git, through sessions and changes of branch, until they are flushed explicitly. Git supplies the committed versions of the nodes. When the working files have changed since a spotlight was taken, the editors say so as advice and go on highlighting the nodes by their IDs.

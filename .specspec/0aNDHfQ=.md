---
id: 0aNDHfQ=
type: requirement
parents:
- 3V6SdSA=
- rvz48KY=
---
# Reload the spotlight list on its own events, apart from reloads of the graph

The list of spotlights is loaded when a view opens, on Refresh, on configured polling and on the coalesced notifications of the spotlight store itself. An automatic synchronization that concerns the graph alone reads the node files and leaves unchanged spotlight metadata unread. The first load sets the baseline for arrivals, the store is watched in comparisons between commits as well, a list that failed to load is read again, and an arrival leaves editing, cameras and drafts as they are.

Reads of the list by concurrent callers share one read in flight and at most one follow-up that an event requested. Polling requests the refresh of the graph and the refresh of the spotlights independently and is off by default. Every explicit change is validated against the current node files.

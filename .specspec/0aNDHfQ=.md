---
id: 0aNDHfQ=
type: requirement
parents:
- 3V6SdSA=
- rvz48KY=
---
# Refresh Spotlight metadata from its own events

Load the retained Spotlight list on opening, explicit Refresh and configured polling,
and from its own coalesced store notifications. Graph-only automatic synchronization
reads canonical context without rereading unchanged Spotlight metadata. The first-load baseline, historical-view watching, retry after list errors and arrival preservation of native editing, cameras and drafts hold here too.

Coalesce list reads across concurrent callers into one in-flight read and at most
one event-driven follow-up. Polling requests graph and Spotlight refresh independently
and is off by default. Explicit mutations run fresh canonical validation.

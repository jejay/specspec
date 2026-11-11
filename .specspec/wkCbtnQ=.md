---
id: wkCbtnQ=
type: requirement
parents:
- tvic3PQ=
---
# Stop polling without stopping watchers, and verify shutdown with controlled clocks

Polling is off by default, and an interval of zero stops the periodic ticks. The watchers for files, Git and spotlights stay active, Refresh stays available, and coalesced work that was already requested can complete. The first asynchronous discovery of the Git paths gives a legitimate hint to refresh whenever it finishes. Closing a view first applies the document edits that the view has received, then disposes the timers of its session and guards against watcher events and read results that arrive late.

The tests of these boundaries use controlled virtual clocks for timeouts and intervals, explicit gates on reads and a real `GitWatcher` whose discovery the test controls. They await the completion of each operation and of the disposal, and they assume no fixed quiet period of wall-clock time in which every producer would have settled. Where it matters they count requests for the graph and requests for metadata separately. They cover a discovery that finishes after polling is disabled, active reads with coalesced follow-ups, the replacement of an interval, comparisons between commits and a view that closes while its discovery is pending. Separate integration tests run against real Git and real filesystem watchers.

The hooks for timers and for discovery belong to the test fixture. In these tests the product runs with its own debounce, retry and startup timing, its operation deadlines, polling off by default, its watcher notifications, saving by VS Code and its production scheduling. A regression is shown by reproducing its cause and by running the suites concurrently and repeatedly, with every valid watcher refresh enabled and every sleep at its length.

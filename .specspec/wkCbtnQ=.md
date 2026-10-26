---
id: wkCbtnQ=
type: requirement
parents:
- tvic3PQ=
---
# Verify polling shutdown independently of watcher completion

Polling defaults off and configuring zero stops periodic ticks. File/Git/Spotlight
watchers remain active, explicit Refresh remains available and already-requested
coalesced work can complete. Initial asynchronous Git discovery supplies a legitimate
refresh hint whenever it finishes. Closing a view drains its received native edits,
then disposes session timers and guards against late watcher/read delivery.

Test these lifecycle boundaries with controlled virtual timeout/interval clocks,
explicit read gates and controllable real GitWatcher discovery. Await operation and
disposal completion rather than assuming all producers settle within a fixed wall
clock quiet window. Count graph versus metadata requests separately where relevant.
Cover delayed discovery after polling is disabled, active reads and coalesced
follow-ups, interval replacement, historical targets and closing with discovery
still pending. Preserve independent real Git/filesystem watcher integration tests.

The timer/discovery seam belongs to the test fixture. Product debounce/retry/startup
and operation deadlines, default-off polling, watcher notifications, native save
ownership and production scheduling retain their existing semantics. Causal failure
reproduction and concurrent/repeated suite runs supply regression evidence rather
than suppressing valid watcher refreshes or extending arbitrary sleeps.

---
id: _LWxOi0=
type: requirement
parents:
- evfMtUM=
---
# Keep watcher tests independent of platform timing

On macOS a directory watch starts shortly after it is requested and delivers reports
in batches. A change made at that moment can go unreported, and one made just before
the watch can still be reported. On Linux and Windows the watch exists when the
request returns.

A test that scripts Git replies or counts reads scripts its file-system hints too and
sends them itself. A test of real watching waits 200 ms after a watch begins before
it changes a file or records a baseline.

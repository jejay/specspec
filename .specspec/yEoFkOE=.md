---
id: yEoFkOE=
type: requirement
parents:
- 3V6SdSA=
---
# Discover Git watch paths asynchronously and coalesce notifications

Resolve private/common Git metadata paths with a bounded asynchronous Git command.
Coalesce discovery requests while one command is active, then adopt only current
results. Keep each command within three seconds; retry transient failures up to
three attempts with 200/400 ms waits. Reuse valid watches during retry, and report
an exhausted failure. Root metadata identity avoids redundant discovery on ordinary
index/ref changes. Keep the host event loop responsive for renderer acknowledgements, source
previews and native documents. Watch HEAD and shared refs with the existing
bounded directory watches and reattach after replacement, including linked worktrees.

Treat non-Git folders as supported, surface real discovery failures, and dispose
pending discovery without late watches or reload notifications. Git reads preserve
index/ref ownership; filesystem hints continue to trigger fresh backend reads.

Both hosts use this shared HEAD/ref notification path. Index stat-cache writes
and Git-extension status events leave HEAD-to-working presentation unchanged.
Canonical file notifications cover working text; staged source actions and checks
read actual current index bytes at invocation. Preserve stage/commit ghost behavior.

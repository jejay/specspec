---
id: yEoFkOE=
type: requirement
parents:
- tGpRMLM=
- tvic3PQ=
---
# Discover Git watch paths asynchronously and coalesce notifications

The private and the common metadata directory of the Git repository are found with an asynchronous Git command that is limited in time and output. While one command runs, further requests for discovery are coalesced, and a result is adopted only when it is current. Each command has three seconds. A failure that may pass is retried, up to three attempts with waits of 200 and 400 ms; valid watches stay in use during the retries, and a failure after the last attempt is reported. The identity of the `.git` entry at the project root tells whether a discovery is needed, so that ordinary changes of the index and of refs start none. The event loop of the process that hosts the editor stays free for render acknowledgements, source previews and editor documents. HEAD and the shared refs are watched through watches on single directories, which attach again after a replacement, in linked worktrees as well.

A folder without Git is supported. A real failure of discovery is shown. A discovery that is pending when its view closes is disposed and leaves neither a late watch nor a late reload notification. Reading Git leaves the index and the refs in the hands of Git, and hints from the file system lead to fresh reads by the backend.

Both graph editors use this shared path for notifications about HEAD and refs. Writes to the stat cache of the index and status events of the Git extension leave the displayed comparison of HEAD with the working files as it is. Notifications about node files cover the working text, and staged source actions and checks read the actual bytes of the index when they are invoked. A deleted node stays visible when its deletion is staged and disappears when it is committed.

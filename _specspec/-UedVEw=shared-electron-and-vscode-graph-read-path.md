---
id: -UedVEw=
type: requirement
parents:
- 0dvOn3A=
- YOPhqYc=
- PL1IogE=
- VDss3KM=
- L0KGXB8=
---
# Share graph reads across both hosts with optional document overlays

Both Electron and VS Code use one shared project read/comparison coordinator and
backend operation. Electron supplies saved files; VS Code additionally supplies its
actual native document overlays. Historical targets bypass workspace buffers. Share
bounded verified baseline hints, identical in-flight reads, isolated per-view payloads,
project disposal and working-first startup followed by explicit comparison adoption.
Ongoing full refreshes use one comparison request rather than export plus diff.

Keep the first working phase explicitly provisional; preserve later input, camera,
focus, drafts and render membership acknowledgements. Current-file failures retain
marked last-valid context; comparison failures leave usable current context with a
clear unavailable note. Watch events remain hints and explicit refresh is current.
Project switches dispose caches and reject stale generations/text versions.

Read/compare is separate from native document edit planning and managed persistence.
Native plans remain non-writing and VS Code owns document application/Save/undo.
Electron/project actions retain the managed writer. Shared reads do not install a
server, introduce a persistent worker, or weaken fresh mutation and exact-index checks.

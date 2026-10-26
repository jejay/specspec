---
id: PfJv45U=
type: requirement
parents:
- 3fWBW_g=
- evfMtUM=
---
# Use reproducible host poses and measured aggregate test budgets

Shared real-host geometry/gesture probes use the supported reduced-motion preference;
normal-motion camera behavior has independent unit coverage. Isolated Electron and
VS Code test launches disable background/renderer/occlusion timer throttling. Attempt
foregrounding independently of optional browser-window sizing. Preserve production
camera/renderer behavior and individual pose/source/form/ink/watcher/request deadlines
and assertions.

A shared test-harness budget module allows 300 seconds for the expanded shared UI
phase and 160 seconds for native lifecycle. Reserve 40 seconds for host startup and
shutdown, and 60 seconds for Electron's persisted-reload/revision phase. Electron's
aggregate guard is 400 seconds; VS Code's is 500 seconds. Test their relationships
and both runners' use of them. These bounded aggregate allowances account for all
backchannel contexts, actual CLI/Git exact deletion and repair, recovery, reload and revision checks.
They do not redefine production responsiveness or individual operation deadlines.

Report aggregate guard expiry explicitly. Closed CDP transports fail pending calls
promptly instead of manufacturing an unrelated evaluation timeout. Record full-run
elapsed measurements and actual passed/failed phases with platform scope; individual
operations continue to fail under their existing deadlines.

Test-created HEAD snapshots contain every referenced parent. When staging a
coherent deletion/repair slice, choose shared outside parents already present in HEAD, and validate
the complete exact index before each fixture commit. This is fixture construction
discipline; owners retain ordinary coherent multi-file staging and commit control.

Observe asynchronous host dialog readiness before asserting visibility. Electron's
post-reload comparison check uses the same bounded 30-second readiness polling as
its adjacent draft/list restoration checks, within the existing outer allowance.
Retain the actual dialog-open, revision-target and read-only/workspace assertions;
production operation and other individual test deadlines keep their own contracts.

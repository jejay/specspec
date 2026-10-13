---
id: PfJv45U=
type: requirement
parents:
- 3fWBW_g=
- evfMtUM=
---
# Use reproducible host poses and consistent aggregate test budgets

Shared real-host geometry/gesture probes use the supported reduced-motion preference;
normal-motion camera behavior has independent unit coverage. Isolated Electron test
launches disable background/renderer/occlusion timer throttling so intrinsic resize
work runs in the test window. Preserve production camera/renderer behavior and all
individual pose/source/form/ink/watcher/request deadlines and assertions.

A shared VS Code test-harness budget module provides 160-second aggregate guards
for shared UI and native lifecycle phases. The outer process guard is their sum
plus 40 seconds startup/shutdown, 360 seconds. Test this relationship. Record actual
results and failed attempts in Git/diagnostics. These are reproducibility choices
for bounded checks; responsiveness is assessed separately under runtime conditions.

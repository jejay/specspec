---
id: PfJv45U=
type: requirement
parents:
- AuhoBoU=
---
# Make the outer VS Code smoke budget cover its existing two phase guards

The cascade task's unchanged VS Code runner passed the complete graph/cascade
checks twice, then was killed by its 240-second outer timer during native-document
checks (different node tab). Its shared and native phases already have separate
160-second aggregate guards. The unchanged native-only run passed. This exposes
an inconsistent outer budget; it does not prove scheduling the only possible
cause of every native timeout or certify production performance.

Choose a shared test-harness budget module: preserve each 160-second phase guard,
and make the outer process guard their sum plus 40 seconds for startup/shutdown
(360 seconds). Test that relationship to prevent future drift. Do not alter any
individual CDP/request/watcher/mapping/native-document deadline, assertion,
production camera/renderer or default host polling. Run a fresh complete suite;
record both previous failed profiles and the actual outcome. A bigger aggregate
test budget is neither a UI responsiveness guarantee nor weakened semantic proof.

Origin: separate revisable verification-environment conclusion implementing the
full host checks of AuhoBoU=, based on dispatched failures rather than a user
request to change production timing. Keep the earlier reduced-motion/isolated
Electron choices and ordinary-animation unit coverage separately documented.

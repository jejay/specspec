---
id: sxxzsrk=
type: requirement
parents:
- 3V6SdSA=
- L0KGXB8=
---
# Reuse bounded per-project application channels

Hosts reuse two shell-free Python application processes per active project and
trusted executable configuration: an ordinary API channel and an independent
read-only source-preview channel. Warm both at the first authorized request.
The hidden api --stream transport reads bounded newline-delimited API 7 requests
and emits one ordinary API 7 envelope per request. The one-shot CLI remains usable.

Serialize frames per channel, bound queued requests and input/output/time budgets,
and isolate configuration/project changes. Each request performs current backend
validation and fresh file/ref/index reads under the existing caching rules. Share
only interpreter lifetime; retain native-plan and canonical mutation ownership.

Dispose channels on final project close/switch. A failed channel rejects pending
work; recreate only for a later deliberate request. Dispatched mutation failures
report uncertain outcome for inspection, and queued/unstarted requests stay distinct.
Mutations receive one execution, with no automatic replay. Match complete UTF-8
frames, diagnose malformed/unsolicited/oversized output, and keep stderr bounded.

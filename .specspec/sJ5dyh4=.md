---
id: sJ5dyh4=
type: requirement
parents:
- 0dvOn3A=
---
# Render concise readable results by default

Use plain readable text and Markdown for terminal and LLM callers, independent of
redirection. Node listings contain full IDs, types, headings and relationship summaries;
single-node and ancestor-completed query reads show labelled metadata and complete binding bodies. Ancestor-completed queries
include required ancestors in deterministic graph order and clearly identifies
optional surrounding IDs without unexpectedly dumping their bodies. Explicit byte
budgets count the actual representation and fail rather than truncate required text.

Mutations identify changed nodes by full ID and report affected scope and warnings;
checks report counts and diagnostics. Keep stdout for results and stderr for human diagnostics. Escape
terminal control characters visibly without executing project text. Preserve meaningful content whitespace and native before/after byte ownership.
Logical node records and review patches use LF; encoding-only changes remain quiet.
Raw reads, original-byte transaction checks and recovery retain physical evidence. Machine mode is explicit
--json; pipes do not silently switch representation and there is no LLM-only interface.

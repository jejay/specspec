---
id: KGvVHh0=
type: requirement
parents:
- 3V6SdSA=
---
# Retry superseded reads without diagnosing invalid files

A completed read whose actual document stamp or project generation changed is
superseded, distinct from an invalid specification, unavailable source or closed
project. Discard its result. Retry a bounded number of times within each refresh;
when ongoing change exhausts an automatic refresh, coalesce a follow-up through the
existing event queue. Preserve the displayed graph, native forms, caret, cameras,
highlights and action eligibility while awaiting a current result. Explicit working reads
report supersession and request a follow-up rather than claiming file invalidity.

Only actual current-read/validation failures enter the marked last-valid repair
state. Preserve existing mutation preflights, trust, version checks, writer guards,
per-operation deadlines and default-off polling. Dispose pending retry work when
the session closes. Spotlight publication and other notification bursts retain
these same rules; notification generation is evidence to reread, not a diagnosis.

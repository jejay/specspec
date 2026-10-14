---
id: 3V6SdSA=
type: requirement
parents:
- tGpRMLM=
- GQdmCrA=
- tvic3PQ=
---
# Share identical in-flight project reads and reuse native bootstrap context

Coalesce concurrent reads with the same project, base, generation and actual open-
document text/version/dirty/EOL stamp. Give each view its own presentation payload.
Recheck stamps after loading and before adopting bootstrap context; changes cause
fresh reads. Dispose project state on final close. Native bootstrap supplies the
first working snapshot when usable, with asynchronous custom-editor wiring and a
fresh comparison phase. Invalid documents retain their established repair behavior.
Notifications remain hints; ongoing refreshes reread files and resolve current refs.
Explicit Refresh performs a current read. Managed actions retain fresh validation,
project-wide dirty guards, writer locking and reviewed deletion rechecking.

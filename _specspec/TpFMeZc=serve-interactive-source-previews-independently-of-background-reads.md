---
id: TpFMeZc=
type: requirement
parents:
- VnSF9BE=
- tGpRMLM=
---
# Serve interactive source previews independently of background reads

Resolve a clicked read-only source through an independent per-view request lane.
Capture its published render token, displayed node and immutable comparison commit
before asynchronous work. Validate the render token against the published view;
pending comparison choices and mutation preflights retain the displayed context.
Keep working-file previews current and retain ordinary trust, input/output and
operation budgets. Background graph or Spotlight reads can proceed while a source
preview resolves; canonical mutations and native plans retain their serial owners.

Match replies to the latest source request and displayed context. Navigation,
revision adoption, a newer request or disposal invalidates obsolete replies.
Bound source work to one in-flight request plus the latest pending request, replacing
older pending requests. Report current failures explicitly and keep previews literal.

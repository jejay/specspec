---
id: TpFMeZc=
type: requirement
parents:
- VnSF9BE=
- tGpRMLM=
---
# Serve interactive source previews independently of background reads

A click on a source opens a read-only preview, which is resolved on a request lane of its own for each view. Before the asynchronous work starts, the request records the token of the published rendering, the displayed node and the immutable commit of the comparison. The token is validated against the view as it is published, so that a comparison which is being chosen and the read before a change leave the preview in the displayed context. A preview of a working file shows its current content, and the ordinary rules of trust, the limits on input and output and the budgets of operations apply. Reads of the graph and of spotlights in the background go on while a preview resolves, and changes to node files and plans for editor documents keep their own serial order.

A reply is matched to the latest source request and to the displayed context. Navigation, the adoption of a revision, a newer request and disposal make an older reply obsolete. Source work is limited to one request in flight and the latest pending one, which replaces older pending requests. A failure of the current request is reported explicitly, and a preview shows the source text literally.

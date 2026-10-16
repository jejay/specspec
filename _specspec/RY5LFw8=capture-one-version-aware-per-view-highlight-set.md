---
id: RY5LFw8=
type: requirement
parents:
- 7UOmpHw=
- 63jO49Q=
---
# Capture one version-aware per-view highlight set

Use the cycle red, blue, green, purple, turquoise, yellow, then off. A custom
spotlight ink advances to red. Accept Ctrl+Shift or Meta+Shift as direct removal;
Command is the macOS Meta key. These gestures on node chrome consume the click
without focusing a node or moving the camera. Native inputs, text selection,
links and form buttons retain their normal modified clicks. Anonymous new-node
cards have no capturable identity. A modified click on a changed node starts red.

Keep one per-view map of full node ID to exact blob and color, shared by manually
painted and spotlight-applied highlights. Selecting a spotlight replaces this map
with its exact matches; the whole-map clear applies to both origins. Snapshot or
list arrivals preserve the map. Paint only exact currently displayed versions;
other selected versions remain in the map across navigation and reload. Flush
removes the retained store while the editable highlight set remains independently
clearable. Persist only references/colors as presentation state, not node bytes.

A local modal asks for a nonblank message of at most 500 characters, with Cancel
and Create actions. Freeze the selected refs for submission. Save groups by color
as one new immutable shot, using the existing locked atomic publisher. Resolve
exact bytes from retained spotlight blobs, the selected target/base snapshots or
native document overlays supplied by the trusted host. Reject unavailable or
changed versions atomically, retaining highlights and the message for retry.
Managed unsaved form text stays a draft; native overlays retain their actual bytes.
An assembled shot uses highlights provenance instead of claiming all members came
from one commit. Existing shots retain their bytes and meaning. Creation preserves
the highlight set, drafts and camera, and refreshes the shared retained list.
Workspace trust and host allowlists guard this local write in both live and
historical views. Canonical node schema retains its fields.

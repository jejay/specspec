---
id: RY5LFw8=
type: requirement
parents:
- 7UOmpHw=
- 63jO49Q=
---
# Keep one set of highlighted node IDs per view and create spotlights from it

Each view keeps one ordered set of full node IDs, shared by the highlights set by hand and the highlights applied from a spotlight. A Shift-click on a card toggles its membership, and a click with Ctrl or Meta and Shift removes it directly. On a card outside its inputs and controls the gesture is consumed and moves neither the focus nor the camera, and the inputs and controls inside a card keep their ordinary clicks with modifier keys. The card of a new node, which has no ID yet, cannot be highlighted.

Selecting a spotlight replaces the set with all IDs of the spotlight, switches to its comparison and frames the nodes that are available. A card is painted by its node ID, whether it survives in the target or is a deleted node of the base, and also when its version has changed. An ID without a card stays in the presentation state through refresh and navigation. A flush of the spotlights leaves the editable set as it is until it is cleared explicitly. The presentation state of a view stores the IDs and the ID of the active spotlight, and no node text.

A modal dialog freezes the selected IDs and asks for a message that is not blank and has at most 500 characters, with the buttons Cancel and Create spotlight. The session of the editor, which checks authorization, supplies the comparison on display and the unsaved text of open editor documents. The selected IDs are validated against both sides of the comparison before the metadata is published atomically. After a failure the message and the highlights are there for another try. Creating a spotlight leaves drafts and camera as they are and saves neither an editor document nor a form.

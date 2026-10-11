---
id: 51c3e963-674e-4d5d-bd7a-b8d63649e1c8
type: requirement
parents:
- adb5a4c8-f9c5-4bcc-b38b-8584d469cf25
- aee203cc-e68a-4b0d-af18-9920e5303e49
---
# Visualize workspace and revision graph deltas

The visual graph editor works alongside VS Code's Git integration. Users can
inspect changes between the workspace and the last commit, and compare the
specification graphs in different commits.

Origin: [INTENTION_SPEC.md](../INTENTION_SPEC.md), Git-aware visual editing.


Make node version-control differences easier to recognize: color the title and show a matching bottom-right A/M/D cue for added/modified/deleted nodes relative to the selected comparison. Honor configured host theme colors where available and use VS Code defaults otherwise, including standalone windows. Keep semantic fills, linked-source context, rename distinctions and withdrawal separate; a withdrawn file is not deleted and a source-only change is not a modified node.

Origin: the user's title/letter/theme-color correction in this conversation.

---
id: SRsw2W0=
type: requirement
parents:
- eLTZ3sg=
- kpatAr8=
---
# Visualize workspace and revision graph deltas

The visual graph editor works alongside VS Code's Git integration. Users can
inspect changes between the workspace and the last commit, and compare the
specification graphs in different commits.

Origin: [INTENTION_SPEC.md](../INTENTION_SPEC.md), Git-aware visual editing.


Make node version-control differences easier to recognize: color the title and show a matching bottom-right A/M/D cue for added/modified/deleted nodes relative to the selected comparison. Honor configured host theme colors where available and use VS Code defaults otherwise, including standalone windows. Keep semantic fills, linked-source context, rename distinctions and withdrawal separate; a withdrawn file is not deleted and a source-only change is not a modified node.

Origin: the user's title/letter/theme-color correction in this conversation.

---
id: fdB9ZLM=
type: requirement
parents:
- SRsw2W0=
- qnGsij4=
- YOPhqYc=
---
# Use themed headlines and text alternatives without conflating Git states

Map semantic added/changed/removed comparison kinds to A/M/D at the card bottom-right and the same title color in compact/expanded cards. Use gitDecoration.addedResourceForeground and deletedResourceForeground; use editorGutter.modifiedBackground for the requested blue M (VS Code's modified RESOURCE foreground is often amber). Use current CSS theme variables automatically and VS Code dark defaults as fallback/Electron values. Keep rename R distinct in blue and source-only text/context separate without inventing M. Preserve withdrawal, existing Git classes/edge dashes, semantic fills and accessible full state labels. Color changes do not alter graph metadata, layout, drafts, camera or draft baselines.

Origin: the user's cross-platform/sidebar/branding request in this conversation. Technical choices remain revisable.

---
id: 037c4383-1934-4181-96e5-9fc3b2958e2f
type: requirement
parents:
- 51c3e963-674e-4d5d-bd7a-b8d63649e1c8
- 1f2e42c3-331f-4c1c-adc7-897f9bf2e004
- 65f28474-18be-46f8-89f6-b9ce30a0ec96
managed_hash: 7c6d7371daf62363fed330c7cd90f423fcdfd926e15cd9376ee20ab30664c7fc
---
# Use themed headlines and text alternatives without conflating Git states

Map semantic added/changed/removed comparison kinds to A/M/D at the card bottom-right and the same title color in compact/expanded cards. Use gitDecoration.addedResourceForeground and deletedResourceForeground; use editorGutter.modifiedBackground for the requested blue M (VS Code's modified RESOURCE foreground is often amber). Use current CSS theme variables automatically and VS Code dark defaults as fallback/Electron values. Keep rename R distinct in blue and source-only text/context separate without inventing M. Preserve withdrawal, existing Git classes/edge dashes, semantic fills and accessible full state labels. Color changes do not alter graph metadata, layout, drafts, camera or fingerprints.

Origin: the user's cross-platform/sidebar/branding request in this conversation. Technical choices remain revisable.

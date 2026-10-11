---
id: 65f28474-18be-46f8-89f6-b9ce30a0ec96
type: requirement
parents:
- 5563649e-f76e-4c59-8e1d-52f60be938ee
- 6c457b0a-654e-4545-a4b4-667f467be4f3
- fbaee7c1-4c20-47ab-afd2-ae0503d428b5
---
# Share a local renderer and guarded host session through narrow adapters

Extract graph-ui-common as the single source for native DOM/SVG rendering, camera/metrics/layout, HTML/CSS, bounded shell-free Python CLI invocation and serialized message/session handling. Use small host adapters for messaging/state, project discovery/selection, trust/confirmation, revision input, watchers, themes and asset URLs. Use API 3 without fingerprints or managed hashes and token-matched complete-render acknowledgements. Build copied runtime assets from that source for self-contained VSIX/Electron output, retaining pinned offline Dagre/D3 license notices; do not keep hand-maintained renderer forks or rewrite in React. Scope persisted state per project to prevent drafts/cameras crossing roots. Future agent adapters use this seam but remain unimplemented.

Origin: the user's cross-platform/sidebar/branding request in this conversation. Technical choices remain revisable.

## Native documents and independent views

The later node-file/editor conclusion splits project-level document coordination from per-view GraphSession state. Optional native-document and overlay-read ports use the non-writing Python planner; default Electron/project ports retain managed CLI saves. Cameras/focus/comparisons are per view as well as project-scoped. Portable code imports neither SDK. Native text persistence and unapplied-form recovery are host responsibilities, not a new renderer or domain-rule fork.

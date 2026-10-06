---
id: 2f6ee5bd-9014-4a0c-8677-53ecbab93f92
type: requirement
parents:
- adb5a4c8-f9c5-4bcc-b38b-8584d469cf25
- 48f77f19-391f-46d0-b06f-ec7530be4575
managed_hash: 7462f69a5e1a378770d263003c08dce1e8eb8585ec1ae4b9047f4a4395971b3a
---
# Show relationship context and potential downstream impact

In a focused subgraph, show each parent's distance to the manifesto. For each
child, show the total size of its downstream subgraph, including grandchildren,
great-grandchildren, and all deeper generations, to convey the potential scope
affected by a change. Do not limit this cue to the next generation.

Derive these cues from graph links; they are context and potential-impact hints,
not stored spectrum scores, new node categories, or a claim that every reachable
node is necessarily invalidated by every edit.

Origin: the user's requested tree UI revision and clarification, 2026-10-04.
Distance and DAG counting conventions remain separately stated conclusions.

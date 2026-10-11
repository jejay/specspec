---
id: 2f6ee5bd-9014-4a0c-8677-53ecbab93f92
type: requirement
parents:
- adb5a4c8-f9c5-4bcc-b38b-8584d469cf25
- 48f77f19-391f-46d0-b06f-ec7530be4575
---
# Show relationship context and potential downstream impact

In a focused subgraph, retain understandable upstream/downstream context, with
minimum/maximum manifesto-distance coloring explained by the selected legend.
Remove repetitive hop-distance text labels from the nodes, including parents and
the expanded selected card. For each child, continue showing the total size of
its downstream subgraph, including grandchildren, great-grandchildren, and all
deeper generations, to convey potential scope affected by a change. Do not limit
this cue to the next generation.

Derive these cues from graph links; they are context and potential-impact hints,
not stored spectrum scores, new node categories, or a claim that every reachable
node is necessarily invalidated by every edit.

Origin: the user's label-removal correction to the earlier tree UI revision and
all-depth impact clarification. Distance and DAG counting conventions remain
separately stated conclusions.

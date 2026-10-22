---
id: 58igdyQ=
type: implementation
parents:
- Rmh2lfc=
sources:
- path: docs/architecture.svg
- path: docs/architecture.md
- path: README.md
- path: tests/test_repository_docs.py
---
# Render and verify the actor-first architecture overview

`docs/architecture.svg` presents the owner and coding-agent entrances, the shared
canvas/host message port, bounded CLI/JSON interface, Python authority and canonical
project files. A live-feedback strip summarizes notification-driven rereads and
render acknowledgements. Focused managed/native persistence lanes and an agent
review loop explain control and Save ownership without an exhaustive module grid.

`docs/architecture.md` expands the workflows, saved-file versus open-buffer reads,
source boundaries and verification seams. The README links this overview.
Repository documentation tests check local Markdown links, accessible self-contained
SVG resources and separately labelled actor/interface/persistence/workflow groups.
Offline resvg overview, smaller-page and section renders support visual inspection
of hierarchy, labels and arrow clearance. This realizes the descriptive map through
documentation and verification; runtime/domain contracts remain in their own nodes.

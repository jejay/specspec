---
id: ezHjLDs=
type: requirement
parents:
- qowy5AI=
- 7tMgRa8=
- GQdmCrA=
- YaXJpGE=
---
# Use exact ID-only paths across creation, editors and maintained history

Canonical node format 7 requires each direct Markdown filename to equal its full
frontmatter ID followed by .md: _specspec/<id>.md, ending in =.md. The validator
checks exact case and spelling. Existing IDs, bodies, parent links and source
reference grammar keep their contracts. API 6 envelopes retain their structure.
Current-only readers diagnose other versions and noncanonical paths explicitly.

Init, add and the library generate their paths solely from the random full ID.
CLI creation accepts binding text, type, parents and applicable sources; visual
creation forms expose those same fields. Readable labels come from binding text.
VS Code discovers **/_specspec/???????=.md and delegates actual validation to Python.
Body and heading changes retain the same path. ID-leading hyphens and portable
casefold collision checks keep their existing protections.

Cut over the working self-graph and tracked example together, preserving IDs and
binding bytes through path changes. Refresh local documentation links, diagrams,
agent planning recipes and editor examples. Reconstruct every maintained Gantt
revision/ref, including earlier/deleted files, through actual current CLI calls;
refresh source anchors, receipts, ledgers, bundle and snapshot together. Validate
working graphs, exact staged graphs/sources, all retained refs and native/managed
creation. Preserve local experiments and unrelated development history.

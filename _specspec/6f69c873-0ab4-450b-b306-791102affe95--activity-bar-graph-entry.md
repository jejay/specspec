---
id: 6f69c873-0ab4-450b-b306-791102affe95
type: requirement
parents:
- adb5a4c8-f9c5-4bcc-b38b-8584d469cf25
- ee57a451-059d-426b-868e-e898c2503082
---
# Open the graph as a large VS Code editor workspace

Make SpecSpec easy to discover and open in VS Code, with the graph in the main editor area rather than confined to a sidebar. Opening a canonical node Markdown file should open its graph context, focused on that node, with raw Markdown still directly accessible. Independent tabs may show different nodes, cameras or commit comparisons. Keep node settings inline, not in a second editing sidebar. Respect VS Code's established navigation and document semantics instead of turning an Activity Bar view selector into a command launcher.

Correction: the user's earlier left-hand-tab request expressed convenient access to a large graph workspace. Subsequent platform discussion established that Activity Bar icons select sidebar containers; hosting the graph there does not meet that outcome. The user explicitly authorized trying file-based custom editors with native VS Code text-document behavior and a working shared Electron experience.

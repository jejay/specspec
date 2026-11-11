---
id: bOXyw00=
type: requirement
parents:
- PL1IogE=
---
# Draw the graph in a local webview that shows project text literally and guards every action

Node cards are DOM elements and relationships are SVG, in a local VS Code webview that runs only scripts carrying its nonce. Project text enters the page through DOM text APIs, so it is shown literally. The renderer and its assets are bundled locally and run under a strict content security policy. The Python backend plans every change to a node's text, parents and sources and validates every change to the node files.

A view of the working files in a trusted project enables the actions that apply: saving, adding, deleting and the source actions. A comparison between commits shows details that are read-only and can be copied. When a reload finds a graph that breaks a rule, the input stays, and the view shows the current broken relationships and their diagnostics. When a load is unavailable, the view keeps the last graph that loaded and marks it as such. The view subscribes to notifications about the node files and about Git. The owner stages, commits and sets up hooks through the normal Git workflow.

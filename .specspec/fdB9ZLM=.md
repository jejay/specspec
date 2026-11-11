---
id: fdB9ZLM=
type: requirement
parents:
- qnGsij4=
- YOPhqYc=
---
# Color the headline and a corner letter of a changed node with the Git colors of the theme

A node that a comparison shows as added, modified or deleted has a headline in the matching Git color and the letter A, M or D in the bottom right corner, on compact and on expanded cards. Added and deleted nodes take the theme colors `gitDecoration.addedResourceForeground` and `gitDecoration.deletedResourceForeground`, and modified nodes take the blue of `editorGutter.modifiedBackground`. The colors are read from the CSS theme variables of the surrounding editor, and a standalone window uses the defaults of the dark theme of VS Code. Each letter has an accessible label that names the state in full. A node whose linked sources alone changed has an informational cue at the node in place of a letter. The fills that carry the color meaning, the line patterns of the links, the layout, the drafts and the camera work independently of these marks.

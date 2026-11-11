---
id: PAkzXxk=
type: requirement
parents:
- -RQn7Ug=
---
# Show an invalid graph as it is in both editors and keep safe forms editable

Both graph editors show the relationships that can be diagnosed in the current files together with the errors of the structure, including stand-in cards for missing endpoints and components that are disconnected or cyclic. A deleted node from the base of the comparison is historical and cannot be saved. A reference to a missing parent stays visible in the current graph after the deleted parent has left the default view with the commit. A comparison between commits is read-only.

The form of a current node that is safe to write and can be identified stays editable. Each save is checked first against the fresh state in the backend and is persisted by its usual owner. The protections of editing apply to an invalid graph as to a valid one: unsaved editor documents are protected, an edit of a missing file is rejected, an overwrite is confirmed, drafts, text cursor and cameras stay, and source isolation and the trust boundaries hold. A document that cannot be read offers a path to repair its raw Markdown. When the transport fails or the format is unsupported, the editor shows the last usable graph and marks it clearly as such.

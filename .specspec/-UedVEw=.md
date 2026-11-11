---
id: -UedVEw=
type: requirement
parents:
- 0dvOn3A=
- VDss3KM=
- L0KGXB8=
---
# Read the graph for both editors through one shared coordinator, with unsaved editor text laid over the files

The desktop app and VS Code read and compare a project through one shared coordinator and one operation of the backend. The desktop app supplies the saved files, and VS Code adds the actual text of its open node documents, laid over those files. A read of a historical target takes no text from open documents. The coordinator shares the verified hints about the baseline, within their size limit, shares one read among identical requests that are in flight, gives every view a payload of its own and is disposed with its project. A view starts with the working graph and adopts the comparison as an explicit second step. A full refresh in a running view is one request that returns the snapshot together with its comparison.

The first phase, which shows the working graph alone, is marked as provisional. When the comparison arrives, the input made in the meantime, the camera, the focus and the drafts are as the user left them, and each phase is acknowledged by the view with the full list of the nodes it rendered. Files that form an invalid graph are shown fresh, with what can be diagnosed. When the current files cannot be read, the view keeps the last usable graph and marks it as such. When the comparison fails, the view keeps the usable working graph with a clear note that the comparison is unavailable. A watch event is a hint to read again, and an explicit Refresh reads the current state. A switch of the project disposes the caches, and a result of an outdated generation or of an outdated text version is rejected.

Reading and comparing are separate from planning an edit of an editor document and from saving through the writer. An edit plan writes nothing, and VS Code applies it to its document and owns Save and undo. Actions in the desktop app and actions on the whole project write through the writer. The shared reads run the backend as child processes of the editor, and every edit and every check of the exact index reads the current files and objects for itself.

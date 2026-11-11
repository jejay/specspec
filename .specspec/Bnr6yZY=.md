---
id: Bnr6yZY=
type: requirement
parents:
- PL1IogE=
---
# Follow edits made outside the editors and keep the owner's unsaved input

Both graph editors follow the changes that are made to the node files outside of them. While they catch up, unsaved text, the text cursor and the camera stay as they are.

The editors show the graph as the files give it at that moment. When it breaks a rule and can still be diagnosed, they show it with stand-ins for the missing ends of links and with the structural diagnostics. A document whose content cannot be read stays reachable as raw Markdown for repair. When the command line gives no answer or the format of the graph is unavailable, the editors keep the last graph that loaded and mark it as such. Saving a node that changed outside while the owner edited it requires a confirmation to overwrite, and changes elsewhere in the graph leave a draft usable. Whether the node files and the state of an editor agree is decided by comparing contents, and the writer guards every write by the original bytes of the files.

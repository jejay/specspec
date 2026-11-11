---
id: 3V6SdSA=
type: requirement
parents:
- tGpRMLM=
- tvic3PQ=
---
# Share one read among identical concurrent requests and reuse the first read of a node-file editor

Concurrent reads are answered by one read when they agree in project, base, generation and the stamp of the actually open documents, which consists of their text, version, unsaved state and newline style. Each view receives its own copy of the result for presentation. The stamps are checked again after loading and before the first read of a node-file editor is adopted, and a change leads to a fresh read. The state of a project is disposed when its last view closes. The read that VS Code makes while it opens a node-file editor supplies the first working snapshot when it is usable; the wiring of the custom editor completes asynchronously, and a fresh comparison follows as a second phase. A document with invalid text stays repairable as in every other read. Notifications are hints: each refresh reads the files again and resolves the current refs, and Refresh performs a current read. An action through the writer validates the current files, requires that no document of the project has unsaved changes, takes the lock of the writer and checks a reviewed deletion plan again.

The same coordinator of reads and comparisons serves the desktop app, with an empty set of editor documents. Both graph editors read afresh and pass verified hints about the base of the comparison. VS Code alone supplies the overlay of open documents, the first read of a node-file editor and the editing and saving of documents by the editor itself.

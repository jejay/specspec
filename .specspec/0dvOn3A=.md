---
id: 0dvOn3A=
type: requirement
parents:
- ME4UXTA=
---
# Let owners and agents read, change, check and review the specification with a few commands

From the command line an owner or a coding agent reads the specification, changes it, checks it and reviews what changed between two revisions. Someone who uses it only now and then learns it quickly: the commands are few, a result is readable text by default, and every result has a structured form with a predictable shape for programs. A change to the specification can be understood in full on three levels: the nodes that changed, the links that changed and the literal text that changed.

Both graph editors get their data through this command line. They respond promptly and behave alike, because both rely on the one Python backend as the authority.

The command line keeps to what holds everywhere in the product. A node is named by its full ID, an uncertain source link is reported as uncertain, and a graph is checked against the current node format. A VS Code document is saved by VS Code, the writer changes node files in recoverable transactions, and the details of a node deleted since HEAD stay readable.

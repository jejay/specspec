---
id: WpYvGUo=
type: requirement
parents:
- 1T-fMcs=
---
# Distribute the command line as a Python application that a user installs once for all projects

specspec is a Python application with the command `specspec`. A user installs it once, and the command is then available in the directory of every project. Its dependencies live in an environment of their own, isolated from the runtime of each project. People and the graph editors normally rely on such a persistent installation, and a one-shot run through `uvx` works as well. An integration can also import the package as a Python library. The command line needs Python 3.11 or newer and uses Git for its versioned operations.

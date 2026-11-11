---
id: DFS2oJM=
type: requirement
parents:
- WpYvGUo=
- PL1IogE=
---
# Build the command line, the VS Code extension and the desktop app as separate products from one repository

One repository holds the sources of all three products. The command-line tool is built with Python packaging, and the shared renderer, the VS Code adapter and the Electron adapter are built in one private npm workspace. A single npm lockfile at the root and the root scripts install the dependencies, run the tests and the builds, package the VSIX locally and create a portable Electron archive for the current platform. The Python wheel and the source distribution include the initialization guide as a package resource. The VSIX and the desktop package contain the compiled shared code, their local assets and the license notices of their dependencies. Python and Git are prerequisites outside every package, which the user installs. The command line runs with Python and Git alone, and Node and Electron are needed only for the editors.

The VS Code extension is distributed as a VSIX that is built locally. It installs with the ordinary local install command or dialog of VS Code, and starting it with F5 is an optional workflow for developers. The desktop app runs from source or from the portable package of the current platform. Both editors run the `specspec` executable on the `PATH` by default, and explicit settings name another trusted executable. The packaging tools collect only the files that the runtime needs, and they check the contents of each artifact and that all versions agree.

Building is separate from publishing, signing, tagging and committing. CI builds artifacts and uploads them without publishing anything, without installing hooks for the owner and without changing the owner's installed extensions. The documentation tells the platforms on which a product was tested from the targets on which it has not been run.

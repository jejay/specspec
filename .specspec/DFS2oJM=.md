---
id: DFS2oJM=
type: requirement
parents:
- 1T-fMcs=
- WpYvGUo=
- PL1IogE=
---
# Build separate installable products from one private workspace

Use Python packaging for the globally installed CLI and a private npm workspace
for the shared renderer, VS Code adapter and Electron adapter. A single root npm
lock and root scripts provide dependency installation, tests, builds, local VSIX
packaging and current-platform portable Electron archives. Python wheels and source
distributions include the initialization guide as a package resource. UI packages
contain their shared compiled code, local assets and dependency license notices;
Python and Git remain external prerequisites. CLI users need no Node or Electron.

The VSIX installs with VS Code's normal local install command or UI; F5 remains an
optional developer workflow. Electron runs from source or a current-platform portable
package. Both default to the installed specspec executable on PATH, with explicit
trusted executable settings available. Packaging tools collect only intended runtime
files and validate artifact contents/version alignment. CI can build and upload
artifacts without publishing, installing owner hooks or modifying owner extensions.
Documentation distinguishes tested local platforms from unexecuted targets.

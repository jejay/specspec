---
id: Es6S-yg=
type: requirement
parents:
- WpYvGUo=
---
# Install the command-line tool from PyPI by default

The `specspec` distribution on PyPI is the normal source of the command-line tool, so that people and coding agents install it directly with one command. The recommended command is `uv tool install specspec`, and `pipx install specspec` is the isolated alternative to it. The user guides, the agent guide and the screens that a graph editor shows when the command line is missing recommend this installation. The guides explain how the command gets onto the `PATH`, how to upgrade, and that in a remote workspace the command line is installed on the workspace host.

An installation from a local checkout, from a Git URL or from a built wheel is an explicit alternative, meant for development and for qualifying one particular artifact. The graph editors are installed independently of the command line.

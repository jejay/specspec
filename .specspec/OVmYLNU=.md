---
id: OVmYLNU=
type: requirement
parents:
- IMRW29M=
---
# Write through a linked instructions file to the file it points to

An instructions file that is a symbolic link is read and changed where it points, so a project that links AGENTS.md and CLAUDE.md to each other holds one guide in one file. The link target is a regular file inside the project and outside .specspec. For a link to a missing file, a directory or a file outside the project, the command names the problem and writes nothing.

---
id: _wJJQko=
type: requirement
parents:
- ME4UXTA=
---
# Keep the node files and the tools' local working data together in the project

One directory of the project holds everything that specspec keeps there. The specification is one Markdown file per node, directly in that directory. The working data of a single checkout has a reserved place inside the same directory: locks, journals, spotlights, caches and diagnostic files. The specification consists of the node files alone, in the working files, in the Git index and in every commit.

---
id: L0KGXB8=
type: requirement
parents:
- tGpRMLM=
- Yfy0414=
---
# Reuse Git bytes and parsed frontmatter from caches that are verified at every use

Transient caches of limited size hold derived data for a project, for a request or for the loaded library, around the snapshot and graph structures. Every read resolves the refs anew and verifies the entries of the tree or of the index and the metadata of the objects. A graph editor may hand back the immutable bytes of a baseline, within a size limit, as a hint for a warm read. Each hint is verified against the Git blob ID of the current read before it is used, a blob whose hint does not match is fetched in the normal way, and a missing object is reported as missing. A hint belongs to one repository, one subtree and one resolved commit: when HEAD moves the hint stops applying, and staging leaves it applicable because HEAD holds the same nodes.

The parsed frontmatter is memoized by the exact bytes of the header and the version of the parser, within limits on bytes and on entries, and every use receives a copy of its own that it may change. An edit of the body leaves the bytes and the comments of the frontmatter as they are. The fields of the nodes, the graph, the source paths and the state of lock and journal are validated at each read, against what that read found. An eviction from a cache costs time and changes no result. A cache holds derived data alone: the node files and the conditions of an edit are the same with and without it. The writer checks the current files, and a check of the exact index reads the current objects, each as the authority for its own work. A single run of the command line works on its own, within its limits, with every cache starting empty.

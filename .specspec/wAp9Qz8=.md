---
id: wAp9Qz8=
type: requirement
parents:
- tGpRMLM=
- Yfy0414=
---
# Read node blobs from Git in batches with limits on count, size and time

A snapshot read lists the entries of the current tree or of the exact index with literal, NUL-delimited paths and removes duplicate object IDs before it asks for the objects. Metadata and content are requested in batches of limited size. For every path the read keeps its entry, its mode, its stage with any conflict, its nesting, its size, the availability of its object and the diagnostics of the node format. The type and the size of an object are inspected before its body is read. The read checks that the objects come back in the order asked, that the binary framing is exact, that nothing is truncated and that Git exits cleanly, and it keeps finite limits on the size of a request, on the output and on the time. Repositories with SHA-1 and with SHA-256 object IDs are read alike, and a project without a graph and a HEAD that has no commit yet follow the rules of the empty baseline. A large graph is read in several chunks and in full. A read from Git leaves the checkout, the index, the objects and the refs to the user and uses the objects that are available locally.

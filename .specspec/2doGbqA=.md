---
id: 2doGbqA=
type: requirement
parents:
- jWl96h0=
---
# Read the known Git blobs of a query in one batch for each version of the code

For each committed revision that is compared, `query` takes the Git blob addresses of the linked paths from the regular-file entries of that revision's tree and adds the blobs that the links record as anchors of their regions. It reads these addresses together into the reader's cache of immutable blobs before it resolves a single link. Each address is read once. Every source row stays a row of its own, with the safety checks for its path and with its exact facts: the raw comparison and the classification by the mode of the link. When both selected commits are the same, one reader of that version of the code serves both sides.

A cache lives within one source comparison. Refs and saved files are resolved afresh in every invocation. The bytes of the working tree come from the saved files and never from blob addresses of the index, and an anchor blob is an immutable read from Git. An object that is missing, of the wrong type or too large and a limit that is exhausted are each reported explicitly. An object that is too large reserves no bytes for its content and leaves the admission budget of the batch to the other eligible blobs. The limits for one object, for one request, for mappings, for the search for renames, for entries and paths and for UTF-8 stay in force.

Speed comes from filling the cache of one call in bulk: nothing persists between calls, and the meaning of a source link is untouched. The output of the command line in a fresh process is measured separately from the instrumented costs of reading, of rendering and of Git processes. Tests verify on fixed workspaces of the current format that batched reading gives the same output as reading the blobs one at a time, and they guard the number of Git processes, because a limit on wall-clock time fails by chance. A timing from one machine is reported as an observation, with its platform and the state of its caches, and stands for that machine alone.

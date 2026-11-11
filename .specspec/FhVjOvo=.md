---
id: FhVjOvo=
type: implementation
parents:
- wAp9Qz8=
- L0KGXB8=
sources:
- path: src/specspec/git_objects.py
- path: src/specspec/git.py
- path: src/specspec/git_process.py
- path: src/specspec/format.py
- path: src/specspec/editor.py
- path: src/specspec/workspace.py
- path: tests/test_loading.py
- path: tests/test_git.py
- path: tests/test_editor.py
- path: tests/test_sources.py
---
# Read Git objects in checked batches and reuse verified bytes and parsed headers

`git_snapshot` in `git.py` lists the literal entries of the exact index or of a tree. `read_blobs` in `git_objects.py` asks `git cat-file` for the metadata and for the content of the objects in batches, checks the framing of every answer and the availability of every object and reports a failure for the node path concerned. A batch holds at most 256 objects and a content batch at most 8 MiB, and a batch call ends after 20 seconds. A blob that an editor hands back as a hint is used once the ref, the tree and the object were checked anew and its bytes match the blob ID, which saves reading the same content again. The read operation of the application protocol carries these hints in a field of their own beside the data that a view displays, and `editor.py` accepts and returns at most 2 MiB of them. A moved HEAD and a hint that does not match lead to a read of the current content. `format.py` memoizes parsed headers by their exact text, hands out a separate copy for every use and holds at most 65,536 headers and 16 MiB. The validation of nodes, graph, sources and working state, and the lock, the checks of original bytes and the recovery of the writer in `workspace.py`, run at every read and write on their own authority.

`tests/test_loading.py`, `tests/test_git.py`, `tests/test_editor.py` and `tests/test_sources.py` cover equal results with and without hints, a lost object, malformed framing, reads of the current HEAD and of the index, edit plans for editor documents, the node format, comments, newline styles and Unicode text, the retention of source blobs, and edits with their recovery. The reads of the maintained Gantt history in `tests/test_gantt_git.py` go through the same batches. What is read from Git is derived data: the node files in the current format, the application protocol and a single run of the command line are the authority.

`git_snapshot` resolves an ordinary HEAD directly. Only when that fails does `unborn_head` check, with two further Git calls, whether HEAD is a symbolic branch that has no commit yet. A missing object, a corrupt detached HEAD and an invalid named revision are reported with their own errors. Every read sees a HEAD that has moved and the bytes that are staged at that moment.

Every Git subprocess starts with the command line and the environment that `git_process.py` defines: `run_git_process` for single calls, and `git_command` with `git_environment` for the streamed object batches. They turn off fsmonitor and the display of signatures and disable lazy fetching, optional locks, remote protocols and terminal prompts. A single call runs with standard input closed and with a limit on time and on output for its call site, 60 seconds and 64 MiB unless the call site sets its own. The reads for source impact pass the referenced paths in chunks of at most 8 KiB, so that a command line stays within the limit of Windows. A cached editor read leaves a HEAD file that is not UTF-8 to a fresh Git read, which reports it with its `FORMAT` diagnostic, and a snapshot of the index leaves out the placeholders of an intent to add.

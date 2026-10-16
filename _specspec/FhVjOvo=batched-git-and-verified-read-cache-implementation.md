---
id: FhVjOvo=
type: implementation
parents:
- wAp9Qz8=
- L0KGXB8=
sources:
- path: src/specspec/git_objects.py
- path: src/specspec/git.py
- path: src/specspec/format.py
- path: src/specspec/editor.py
- path: src/specspec/workspace.py
- path: tests/test_loading.py
- path: tests/test_git.py
- path: tests/test_editor.py
- path: tests/test_sources.py
---
# Read canonical Git batches and reuse verified derived data

The Git snapshot reader lists literal exact-index/tree entries, batches bounded
object metadata/content, validates object framing and availability, and maps
errors to each canonical path. Verified immutable byte hints reduce repeated
content reads after fresh ref/tree/object checks. The shared application read protocol holds
these hints outside display data; HEAD movement and mismatched hints cause current
reads. Round-trip header memoization uses exact header text, isolated mutable copies,
and bounded entries/bytes. Node/graph/source/runtime validation and managed writer
locking/original-byte/recovery checks keep their existing owners.

Focused and maintained-history tests exercise cached/uncached equivalence, object
loss and malformed framing, current HEAD/index, native planning, node grammar,
comments/EOL/Unicode, source retention and mutation/recovery. Git read data is
derived; canonical node format 6 / API 6 and the one-shot CLI remain authoritative.

Resolve ordinary HEAD directly. Only a failed resolution checks for a genuinely
unborn symbolic branch; missing objects, detached corruption and invalid named
revisions retain their errors. Fresh HEAD movement and staged-byte checks remain
authoritative while successful reads avoid the two extra unborn-branch processes.

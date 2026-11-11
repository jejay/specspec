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
# Read canonical Git batches and reuse verified derived data

The Git snapshot reader lists literal exact-index/tree entries, batches bounded
object metadata/content, validates object framing and availability, and maps
errors to each canonical path. Verified immutable byte hints reduce repeated
content reads after fresh ref/tree/object checks. The shared application read protocol holds
these hints outside display data; HEAD movement and mismatched hints cause current
reads. Round-trip header memoization uses exact header text, isolated mutable copies,
and bounded entries/bytes. Node/graph/source/runtime validation and managed writer locking/original-byte/recovery checks have their own owners.

Focused and maintained-history tests exercise cached/uncached equivalence, object
loss and malformed framing, current HEAD/index, native planning, node grammar,
comments/EOL/Unicode, source retention and mutation/recovery. Git read data is
derived; canonical current node format / application protocol and the one-shot CLI are authoritative.

Resolve ordinary HEAD directly. Only a failed resolution checks for a genuinely
unborn symbolic branch; missing objects, detached corruption and invalid named
revisions retain their errors. Fresh HEAD movement and staged-byte checks are authoritative while successful
reads avoid the two extra unborn-branch processes.

The `git cat-file` batches of git_objects.py start Git with `git_command` and `git_environment` from git_process. Every other Git subprocess runs through git_process.run_git_process, which turns off
fsmonitor and signature display, disables lazy fetch, optional locks, remote
protocols and terminal prompts, closes stdin and applies per-site timeouts and
output caps. Source-impact reads pass referenced paths in chunks of at most 8 KiB
so command lines stay within Windows limits. The header cache holds 65,536 parsed
headers. Cached editor reads leave non-UTF-8 HEAD files to a fresh Git read with
their FORMAT diagnostic, and staged snapshots leave out intent-to-add placeholders.

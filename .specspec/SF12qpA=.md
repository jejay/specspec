---
id: SF12qpA=
type: implementation
parents:
- 6p7T7CY=
- 7kYVG_E=
- cpFRqIM=
- nIj9fmE=
- 4ZvnSGw=
- aILBxDs=
- ivvUgP4=
sources:
- path: src/specspec/cli.py
- path: src/specspec/output.py
- path: src/specspec/wire.py
- path: src/specspec/application.py
- path: src/specspec/source_commands.py
- path: src/specspec/model.py
- path: tests/test_cli_compact.py
- path: tests/test_api.py
- path: tests/test_deletion.py
- path: tests/test_sources.py
- path: example/gantt/history/verify.py
- path: example/gantt/history/cli.jsonl
- path: example/gantt/history/revisions.json
- path: example/gantt/history/gantt.bundle
- path: docs/cli.md
- path: src/specspec/cli_help.py
- path: src/specspec/annotation_commands.py
- path: tests/test_cli_help.py
- path: graph-ui-common/host/session.cjs
- path: graph-ui-common/test/session.test.cjs
- path: docs/investigations/cli-help.md
- path: graph-ui-common/test-host/fixture.cjs
- path: graph-ui-common/test-host/platform.cjs
- path: src/specspec/workspace.py
- path: tests/test_cli_receipts.py
- path: src/specspec/node_text.py
- path: tests/test_node_newlines.py
- path: tests/test_final_newline.py
- path: vscode/test-host/documents.cjs
- path: tests/test_cli_stdin.py
- path: tests/test_local_state.py
---
# Implement the compact command surface and complete review projection

Click presents seven everyday verbs with focused advanced tools and a bounded hidden
application adapter. Query owns parsed and raw specification inspection, while
cli_help.py supplies concise task guides and a scoped ASCII-safe help formatter.
Host managed preflights use the existing saved API read. Ordinary authoring uses
literal message paragraphs and
combinable add/update/delete steps; absent messages select stdin, and managed UIs send complete text without body flags.
Output rendering separates readable text/Markdown from explicit compact application protocol
envelopes. Structured mutation receipts retain IDs/paths/scope and warnings rather
than full graphs. Readable receipts group full node IDs by Added, Modified, Deleted
and Unchanged, with hypothetical preview labels and explicit alias associations.
The writer records transient invocation actions from locked original/candidate
logical text; output uses the verified transaction result independently of Git status.
Tests cover init, singleton and composed mutations, no-op body/parent/source and
replacement edits, byte-only changes, fresh locked originals, post-write external
edits, preview/refusal, invalid/incomplete context and unchanged protocol fields.
The current node format and canonical identities/source grammar remain stable.

Full review output combines stable-ID classification, every logical canonical
text hunk, relationship labels and separate linked-source context. Comments,
whitespace and EOF changes remain represented while encoding-only changes stay
quiet. node_text.py shares logical normalization and existing-document EOL selection
across comparison, serialization, native planning and action receipts. Raw bytes
remain authoritative for safety, recovery, Git objects and explicit raw reads.
Complete managed/native-plan serialization appends only a missing file terminator
and includes its bytes in limits, preserving trailing blank lines and empty repair
bodies. tests/test_final_newline.py covers the convention and its read/write boundary. API comparisons carry one target plus previous differing/
deleted records and ID-based metadata; projections reconstruct both complete revisions.
Query ancestor completion preserves every chosen parent path. The shared emitter
formats once and budgets actual encoded query output, including envelopes and
terminal-control escaping, before writing a complete result. Read-only source
inspection and deliberate capture/reanchor share the domain resolver and writer.

Tests cover text/control/Unicode output, actual byte budgets, API validation, complete
logical text patches, compact/expanded equivalence, deleted membership through staging/
commit, source retention and exact-index distinction. The Gantt corpus uses actual
current CLI receipts across all retained refs, preserving identities, redirects,
application bytes and positive spec-before-code checkpoints. Guides and diagrams name
the current operations and separate protocol 7 from node schema 7.

Static command help uses ASCII punctuation so Click can render help through legacy
Windows pipe encodings. Readable result/diagnostic and structured envelope emission
retain their explicit UTF-8 byte paths. Subprocess regressions force ASCII/cp1252
stdout encodings for every root/subcommand help without changing canonical project
text. Dedicated tests cover all help paths, removed-command rejection, safe raw
repair/index/history reads and unchanged managed/native mutation ownership.

Hidden integration controls stay out of all help and ordinary query headers omit
internal versions. Tests assert 50–70 percent help-body lengths, automatic stdin
preflight and a project/input-independent capability handshake.

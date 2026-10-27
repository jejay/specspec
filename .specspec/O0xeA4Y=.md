---
id: O0xeA4Y=
type: implementation
parents:
- EcEFfgg=
sources:
- path: src/specspec/body_replacements.py
- path: src/specspec/cli.py
- path: src/specspec/edit_cli.py
- path: src/specspec/batch.py
- path: tests/test_cli_replacements.py
- path: tests/test_cli_chains.py
- path: tests/test_transactions.py
- path: docs/cli.md
- path: docs/investigations/exact-replacements.md
- path: src/specspec/replacement_matching.py
- path: tests/test_replacement_matching.py
- path: pyproject.toml
- path: tests/test_ids.py
---
# Implement source-mapped body replacements through the existing writer

cli.py parses the same repeatable OLD/NEW arguments, rejects mixed body sources
and exposes replacements through the shared explicit-edit planner. edit_cli.py
consumes the complete two-value option arity before callbacks. CanonicalIdCommand
keeps full hyphen-leading IDs out of Click short-option clusters, preserving IDs
containing m alongside the message option. All option values remain literal;
comparison tolerance is a domain rule rather than another input mode.

replacement_matching.py maps LF/CRLF/CR positions to original character boundaries.
A lazy CommonMark/table parser records only source-proven prose spaces and soft
breaks, protecting structural and inline syntax. Both comparison views contribute
to one unique original-span assessment without exact-layout preference. Parser line,
token, nesting and candidate/work guards reject incomplete analysis explicitly.
body_replacements.py resolves all pairs against the same original body, rejects
physical range overlaps and joins unchanged slices with content-literal NEW. The
writer adapts newline encoding to the existing target style. Bounds use actual
target-style bytes after a conservative bounded-construction check.

batch.py retains combined input accounting and fresh under-lock transformation.
The existing serializer, final graph validation, deletion consent, original-byte
checks, journal and recovery retain their owners. Ordinary word/full-body matches
and normal CLI/private API startup avoid the Markdown dependency until needed.
UI transports and API/current node format remain unchanged.

Tests cover line-ending and prose-layout permutations, protected Markdown, Unicode
source boundaries, all-layout ambiguity, duplicate-span handling, literal output,
actual consumed bytes, source conflicts, bounds and parser laziness. Existing CLI
and transaction tests retain previews, invalid states, alias/deletion repair,
concurrency and interruption recovery. Windows subprocesses preserve Unicode argv
under legacy output encodings. The linked investigation records completed evidence
and the bounded qualification scope.

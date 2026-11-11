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
- path: src/specspec/replacement_matching.py
- path: tests/test_replacement_matching.py
- path: pyproject.toml
- path: tests/test_ids.py
---
# Match replacements against the Markdown source and apply them through the writer

`src/specspec/cli.py` parses the repeatable `--replace` with its OLD and NEW arguments, rejects a step that mixes sources for its body and passes the pairs to the planner that all explicit edits share. `src/specspec/edit_cli.py` consumes both values of the option before a command callback runs. Its `CanonicalIdCommand` keeps a full node ID that begins with a hyphen from being read as a cluster of short options, so that an ID containing `m` stays an ID next to the message option. Every option value is literal, and the tolerance of the comparison is a rule of matching, the same for every way text comes in.

`src/specspec/replacement_matching.py` maps positions in text with LF, CRLF and CR line ends back to character boundaries of the original. It loads the CommonMark parser with tables on first need and records only the spaces and soft breaks of prose whose place in the source is proved, which protects structural and inline syntax. The matches of both views of the comparison go into one assessment of unique spans of the original, in which an exact layout has no preference. The analysis of one body with its OLD values is limited to 32,768 lines, 131,072 Markdown tokens, nesting below level 20, 8,192 candidate positions and 67,108,864 steps of scanning and comparing, and beyond a limit it stops with an explicit error. `src/specspec/body_replacements.py` resolves all pairs against the same original body, rejects ranges that overlap physically and joins the unchanged slices with the literal NEW values. The writer adapts the newline encoding to the style of the target document. The size limits are checked on the actual bytes in that style, after a conservative check that bounds the construction of the result.

`src/specspec/batch.py` accounts for the input of all steps together and applies the replacements under the lock, to the freshly read node. Serialization, the validation of the final graph, the consent to deletions, the checks of original bytes, the journal and recovery are the ones that every edit uses. A match of a single word or of a whole body, and the ordinary start of the command line and of the private API, run without the Markdown dependency, which `pyproject.toml` declares.

`tests/test_replacement_matching.py` and `tests/test_cli_replacements.py` cover the permutations of line ends and prose layouts, protected Markdown, Unicode at source boundaries, ambiguity across all layouts, a span that is found twice, literal output, the bytes actually consumed, conflicting sources, the limits and the lazy loading of the parser. `tests/test_cli_chains.py` and `tests/test_transactions.py` cover previews, invalid states, repair with local names and deletions, concurrent writers and recovery after an interruption, and `tests/test_ids.py` covers IDs that begin with a hyphen. Subprocess tests on Windows pass Unicode arguments under legacy output encodings.

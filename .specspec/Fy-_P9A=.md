---
id: Fy-_P9A=
type: implementation
parents:
- BKekD_o=
sources:
- path: example/gantt/history/cli.jsonl
- path: example/gantt/history/gantt.bundle
- path: example/gantt/history/revisions.json
- path: example/gantt/history/verify.py
- path: src/specspec/batch.py
- path: src/specspec/cli.py
- path: tests/test_api.py
- path: tests/test_cli_arguments.py
- path: tests/test_cli_compact.py
- path: tests/test_invalid_workflow.py
---
# Join message paragraphs or read standard input in the command line and pass the text to the shared writer

`src/specspec/cli.py` gives `init`, `add` and `update` the same input: `-m` paragraphs that are joined literally, or UTF-8 text from standard input when there are none, each within the size limit of a node. Which step receives the text of standard input is decided after every step has been parsed and its fields checked. A step with replacements leaves standard input unread, an update of metadata with empty input keeps its body, and nonempty input that more than one step could take is rejected. `src/specspec/batch.py` counts the bytes of the supplied bodies.

The session that both graph editors share sends the complete body on standard input when it saves through the writer, and it names no option for a body. The planning of an edit to a VS Code document and the saving of that document are a separate path. `tests/test_cli_arguments.py`, `tests/test_cli_compact.py`, `tests/test_api.py` and `tests/test_invalid_workflow.py` cover text given directly and by redirection, messages that read nothing, empty and oversized bodies, bodies kept through an update of metadata and the transport through a real subprocess. Invalid and oversized standard input, replacements that leave standard input alone and an ambiguous chain are covered in `tests/test_cli_stdin.py` and `tests/test_cli_chains.py`. Serialization keeps the style of the document, the whitespace that carries meaning and the rule for the end of the file. The receipts in `example/gantt/history/cli.jsonl` are real runs of the current command line over the complete Gantt history, and `example/gantt/history/verify.py` checks them.

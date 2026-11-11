---
id: z3QQuTM=
type: implementation
parents:
- -fXS-dI=
- cpFRqIM=
sources:
- path: pyproject.toml
- path: src/specspec/__main__.py
- path: src/specspec/cli.py
- path: tests/test_api.py
- path: tests/test_core.py
- path: tests/test_ids.py
- path: src/specspec/output.py
- path: src/specspec/wire.py
- path: src/specspec/application.py
- path: tests/test_cli_compact.py
---
# Package the command line, expose its commands and serve the compact application protocol

Hatchling packages `src/specspec` as `pyproject.toml` declares, with the console command `specspec`, and `src/specspec/__main__.py` starts the same command line for `python -m specspec`. In `src/specspec/cli.py` Click exposes the seven everyday commands `init`, `query`, `add`, `update`, `delete`, `check` and `diff` and lists them in the help apart from the advanced tools. The advanced tools for sources and for recovery say explicitly what they change, and they report an uncertain result as uncertain. The hidden command `api` takes versioned requests of the application protocol of at most 16 MiB. Node text comes from literal `-m` or `--message` arguments. Without them a command reads UTF-8 text of at most 1 MiB from standard input, to which a shell redirects a file. A node ID is written in full.

The `query` command hands its selection and `--with-ancestors` to one pipeline in `query.py` and `query_select.py`, which returns the selected nodes complete. `src/specspec/output.py` renders readable summaries of nodes and the review patches of the node files, with the changed relationships and, apart from them, the impact of changed linked sources. The application protocol answers with one compact UTF-8 envelope, built in `output.py`. Its receipts for edits are small, and `src/specspec/wire.py` shapes its comparisons so that both revisions can be rebuilt from them. `src/specspec/application.py` serves the requests of the protocol. The installed tools manage the node format. A byte budget is measured on the representation that was actually chosen, and a reading whose required ancestors exceed it fails as a whole. Control characters for a terminal are printed in a visible escaped form.

Regression tests of the command line and of the graph editors exercise the limits of the protocol and the exit codes, full diffs with every hunk, changed line ends and changed comments, the source operations, deletion with its safeguards, the replacement of parents and IDs that begin with a hyphen. Among them are `tests/test_cli_compact.py`, `tests/test_api.py`, `tests/test_core.py` and `tests/test_ids.py`.

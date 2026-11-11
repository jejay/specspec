---
id: nxNOTwc=
type: implementation
parents:
- J8H7P74=
- ge_uqBs=
- 0ixPI18=
- gdf33gI=
- -r2nyRA=
- ngr7AdE=
- wyrt0hA=
- DIPK_UM=
sources:
- path: src/specspec/templates/AGENTS.md
- path: src/specspec/workspace.py
- path: src/specspec/cli.py
- path: src/specspec/output.py
- path: pyproject.toml
- path: tests/test_initialization.py
- path: tests/test_release.py
- path: tests/test_local_state.py
---
# Package and safely concatenate initialization instructions

The distribution contains one static generic guide, loaded through package resources.
It says what the graph is for in two opening paragraphs, continues with a numbered routine and stays under 12 KB, counted with LF line endings; tests check its essentials,
its size and that every option it teaches appears in visible help. Its concept sections use the outcome/choice and intention/conclusion vocabulary with one example graph. Three owner sentences are worked into an outcome and a choice each, and the passage on what belongs in a node names a list of limits as one decision and says what stays out of the graph. The writing rules show each kind of contrast on an example: an earlier version, the owner's way of working before the product and what the product is not. Each phase names what starts it, including the structure review of the owner's own edits, the implementation phase begins with agent planning, and the report step asks for a spotlight on the nodes discussed.
Initialization validates a single manifesto and safe root instruction target, checks
Git availability and ensures a Git working tree before publishing node/guide bytes,
reusing a containing repository instead of creating nested Git metadata. Git metadata is not claimed by graph rollback. No staging, commit, identity
configuration or hook management is performed.

The workspace lock and bounded byte journal live inside .specspec/local. An absent
guide is exclusively created; an existing regular file retains its exact byte prefix
and receives the template after a separating paragraph. Changed targets reject
publication and recovery. Initialization recovery permits AGENTS.md originals while
ordinary edit journals remain direct-node-only. Direct nodes and the runtime subtree
have separate inventories. Interrupted initialization can recover partial publication.

Tests cover real Git setup and missing/failing Git, invalid bodies, empty/binary
prefixes, unsafe targets, append/create receipts, concurrent changes, publication
interruptions and all-before-any rollback. Package and installed-host checks exercise
the actual template and initialization flow without owner installation.

The existing exclusion helper protects runtime data during initialization.

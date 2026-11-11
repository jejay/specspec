---
id: nxNOTwc=
type: implementation
parents:
- J8H7P74=
- ge_uqBs=
- 4E8Xrp4=
- gdf33gI=
- -r2nyRA=
- ngr7AdE=
- wyrt0hA=
- DIPK_UM=
- 8_eoIEI=
- S1GCPJs=
- 4k0oj5Y=
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
It says what the graph is for in three opening paragraphs, the third on telling intention from conclusion first, continues with a numbered routine and stays under 14 KB, counted with LF line endings; tests check its essentials,
its size and that every option it teaches appears in visible help. Its concept sections use intention and conclusion as the two ends of a link, with one example graph in which a conclusion and then its intention are replaced. The passage on where a statement goes asks what the statement is for and what follows from it, names a list of limits as one conclusion and says what stays out of the graph. Three owner sentences are worked into an intention and a conclusion each. A paragraph after them says that every node except the manifesto can be held against its intentions and that a manifesto's wording can be questioned for conclusions. The writing rules show each kind of contrast on an example: an earlier version, the owner's way of working before the product and what the product is not. Each phase names what starts it. The routine's first step also looks for what the owner committed by hand since the newest agent planning commit. The structure review says that such a commit seals the graph beneath it, has the owner's uncommitted edits committed first as they wrote them, limits remarks on structure to what the owner changed by hand since, and says how sealed nodes are treated. The tandem paragraph leads with telling the owner's intentions from the conclusions they have drawn, has every conclusion held against its intention and ends with guiding questions and tentative answers. The structure review and agent planning include an open manifesto, and the planning summary names the intentions the agent read into the owner's words and its own conclusions. A test holds that the guide uses neither outcome nor choice. Planning is committed on its own, also within the implementation phase, which begins with agent planning, and the report step asks for a spotlight on the nodes discussed.
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

---
id: kiOMI7I=
type: requirement
parents:
- 0dvOn3A=
---
# Read complete specification graphs in a token-conscious tree-shaped view

Give people and coding agents a compact, understandable reading of a specification
DAG through the query command, always in a revision comparison. The ordinary view
compares freshly resolved HEAD with the saved workspace; explicit revisions select
other comparisons. Read the whole graph by default, or an explicitly selected rooted subgraph.
Present each complete selected current binding once, including headless
bodies, and retain complete base bindings for deleted nodes. Sparse hints identify
changes while readers focus on the current specification. Detailed historical text
changes remain available through the dedicated diff command and comparison records.

Identify every direct parent locally in full node headers. Explain source-reference
changes separately from linked-code changes and derived source locations in each
compared version. Treat a source-reference class as the contract for which changes
matter: permitted changes stay quiet, while broken links and uncertainty remain
visible. Keep deleted bindings in the comparison's relationship context.
Read-only exploration preserves canonical files, native buffers and Git state.
The presentation serves human and agent readers with the same information.

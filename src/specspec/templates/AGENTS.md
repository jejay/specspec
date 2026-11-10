# Working with a specspec graph

This project keeps its specification as a specspec graph in `.specspec/`: Markdown nodes that run from the owner's intentions, through the conclusions that serve them, to the implementation that realizes them. Read it to learn why something exists before you change it, and keep it current as you work. The product can be software, a book, a slide deck or any other deliverable.

## Routine

1. Check for owner input: `git status`, the diffs of `.specspec/` and other files (including untracked ones), and `specspec spotlight show` for messages the owner attached to specific nodes. Treat earlier agent work in the working tree as your own unfinished work.
2. Find the relevant nodes: `specspec query --max-distance 2` shows the top of the graph, and `specspec sources show` lists which implementation node links which file.
3. Read each node you act on together with its ancestors: `specspec query ID --max-distance 0 --with-ancestors`. Ancestors bind as much as the node itself.
4. Work in the phase the owner asked for (see Phases). Change the graph only in agent planning or implementation, through `specspec add`, `update` and `delete`.
5. Run `specspec check`, and `specspec check --staged --sources --warnings-as-errors` on the exact index before any commit you are authorized to make.
6. Report what you changed, the choices you made and what remains uncertain.

## The graph

- The **manifesto** is the unique root and states the product's core purpose.
- **Requirements** state outcomes, constraints and choices. Each names the parents it serves; several parents combine reasons.
- **Implementation** nodes are leaves that explain actual artifacts and link them in `sources`.

Each node is one file, `.specspec/<id>.md`, with YAML frontmatter (`id`, `type`, `parents`, `sources`) and a Markdown body. An edge means the child is a reasoned refinement, choice or realization serving its parents. Nodes near the manifesto read as intentions and nodes further out as conclusions: a requirement is a conclusion for its parents and an intention for its children. Position, not a label, carries this.

Ask what should survive if an approach changes, and keep that outcome and each meaningful choice in separate nodes, so a solution can be replaced without erasing its outcome. Neither authorship nor specificity decides the split: an owner may require an exact technology, and an agent may articulate an intention. Split nodes when separate identities allow separate replacement, review or implementation mapping; merge fragments of one coherent decision. Keep the graph shortcut-free: when A reaches C through B, A links only B.

Write node text in positive, present-tense language: what the product is or ought to be now. Git holds earlier versions and the reasons for change, so node text states the current target. To withdraw a node, delete its file and give the reason in the commit message. Requirements describe targets; implementation nodes describe what exists, including its limits. Nodes carry no approval or confidence status: review effort follows uncertainty and impact, and passing checks and tests are evidence rather than proof that the product meets its purpose.

## Phases

**Owner planning.** The owner may edit nodes directly. Before acting, inspect those edits and work out what they mean for intentions and conclusions.

**Tandem planning.** The owner describes what they want and covers breadth; you work out depth. Separate the owner's intentions from the solutions they suggested, challenge weak conclusions, and propose alternatives and your own conclusions. Give a concise overview ready for correction, with guiding questions and your tentative answers, so the owner keeps the lead. Raise planned removals, splits and changes of existing nodes right away; new nodes can wait for agent planning. The graph stays unchanged in this phase, which may take several rounds or be skipped.

**Agent planning** starts when the owner asks you to draw or change the graph. That request authorizes two commits: first the owner's uncommitted specification edits as `Owner specspec changes: <your understanding of them>`, then your result as `Agent specspec changes: <description>`. Build the most implementation-mature graph the available understanding supports, precise enough that implementing it leaves little to guess, and state deliberately open choices as such. Validate the exact index, commit, and summarize changed intentions, choices, gaps and affected nodes.

**Implementation.** Before changing artifacts, read the relevant nodes and their ancestors. Where the graph is too coarse, add conclusions and implementation nodes under the existing intentions; breadth and scope stay with the owner. Keep `sources` and implementation explanations current. When you find a contradiction, implement a simple, broad, contradiction-free subset and report the conflict, your subset decisions and their consequences; a resolution can be proposed on a separate branch.

Code commits, pushes, tags and Git hook changes need the owner's explicit request.

## Commands

Install with `uv tool install specspec` (or `pipx install specspec`) and run commands inside the project, like Git. IDs are full and case-sensitive, including the final `=`. The CLI reads saved files, so save editor buffers first.

```sh
specspec query --max-distance 2                       # top of the graph
specspec query ID --max-distance 0 --with-ancestors   # one node and its justification
specspec query ID --max-distance 1                    # a node and its children
specspec diff                                         # specification changes since HEAD
specspec add --parent PARENT_ID -m '# Title' -m 'Paragraph.'
specspec add --type implementation --parent REQUIREMENT_ID -m '# Realization'
specspec update ID --replace 'old passage' 'new passage'
specspec update ID --parent FIRST_ID --parent SECOND_ID   # replaces the parent list
specspec delete ID --dry-run
specspec check
specspec spotlight show
```

Keep reads bounded with `--max-distance`; an unbounded query of a large graph is long. `-m` values are literal Markdown paragraphs; without `-m` or `--replace`, the body comes from standard input, as in `specspec update ID < body.md`. Several add, update and delete steps can form one invocation: `--as name` names a new node and `--parent '$name'` links to it, `--dry-run` previews the result, and `--require-valid` refuses to write an invalid final graph.

Deletion removes exactly the selected files. Descendants keep their files and their now-missing parent references; resolve those deliberately. The manifesto cannot be deleted. `specspec query --issues --with-ancestors` shows broken states and what they affect.

Implementation sources: `specspec sources capture IMPL_ID PATH --range 10:40 --mode expanding --staged` anchors a line range to the exact staged blob (stage the code first); `--mode strict` reports any change inside the range for review. A whole-file reference is a `- path: FILE` entry under `sources:` in the node's frontmatter. `specspec check --sources` reports links whose code changed, moved ambiguously or disappeared; align the explanation and the code, then run `specspec sources reanchor`.

If an edit is interrupted, keep `.specspec/local/` and run `specspec recover`; use `--force-lock` only after confirming that no other writer is running. Every command has `--help` with purpose, defaults and examples.

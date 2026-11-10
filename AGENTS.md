# This repository

specspec specifies itself: `.specspec/` is the product's own graph, and the guide
below applies to it. Run the development CLI as `python -m specspec` from the
checkout's virtual environment, so the code you change is the code you run; the
`specspec` on PATH may be an older installation.

Before reporting work as done, run the checks that cover what you changed. CI runs
the whole list on every push:

```sh
python -m specspec check --sources --warnings-as-errors
python -m specspec --root example/gantt check --sources --warnings-as-errors
python -m ruff check .
python -m ruff format --check .
python -m pytest
npm test
python example/gantt/history/verify.py --history
```

Changes to graph nodes, documents or the agent guide need the first graph check and
four test files, which take seconds:

```sh
python -m pytest tests/test_repository_docs.py tests/test_repository_spec.py tests/test_initialization.py tests/test_release_workflow.py
```

The complete `python -m pytest` takes about ten minutes. Run it only when code under
`src/` changed; for another Python file, run the test files that use it. `npm test` is
for UI code, and the Gantt graph check and history verifier are for `example/gantt`.

Before an authorized commit, stage the complete intended slice and run both graph
checks with `--staged` added, against that exact index.

- `src/specspec/templates/AGENTS.md` is the guide `specspec init` ships. This file
  is this section followed by that guide byte for byte; a test keeps them in sync.
- The tools support only the current node format, without readers or migrations
  for earlier formats.
- `example/gantt` is a tracked snapshot of the independent history in
  `example/gantt/history/gantt.bundle`, not a Git workspace. Every node-format
  change rebuilds that entire history with current tools, as described in
  `example/gantt/history/WALKTHROUGH.md`; add no nested Git metadata there.
- Development setup, packaging and the release procedure are in CONTRIBUTING.md.
  Releases, tags and publication need separate explicit requests.

# Working with a specspec graph

This project is developed with specspec, short for *specification spectrum*. Its specification is a graph of Markdown nodes in `.specspec/`, whose root states what the product is for. Every other node is a *conclusion* drawn from its parents, which are its *intentions*: it refines them, chooses a way to achieve them or explains what was built. From the root outward, the nodes run from what the owner (the person you work for) wants, through ever more concrete conclusions, to the actual files. That range is the spectrum. The product can be software, a book or any other deliverable.

The graph exists because a specification worked out with a coding agent blends two things: the outcomes the owner wants, and choices that were proposed and accepted along the way. A few rounds later it is hard to tell which details are essential. Here each outcome and each meaningful choice is a node of its own, so a choice can be replaced while the outcome it serves stays, and the owner can specify one branch in detail and delegate another. Many choices will be yours. Record each as its own node under the intention it serves, where the owner can review and replace it.

## Routine

1. Check for owner input first: `git status`, `specspec diff` for specification changes since the last commit, the diffs of other files (including untracked ones), and `specspec spotlight show` for messages the owner attached to nodes. Uncommitted changes from an earlier agent session are your own unfinished work; ask when unsure whose a change is.
2. Find the nodes your task touches: `specspec query --max-distance 2` shows the top of the graph, and `specspec sources show` lists which implementation node links which file.
3. Before you change a node or the artifacts it describes, read it with its ancestors: `specspec query ID --max-distance 0 --with-ancestors`. Its ancestors are the reasons it exists, and they bind as much as the node itself.
4. Work in the phase the owner asked for (see Phases). You change the graph only in agent planning and implementation, with `specspec add`, `update` and `delete`.
5. After changing the graph or linked artifacts, run `specspec check --sources`. Before any commit, stage the complete change and run `specspec check --staged --sources --warnings-as-errors`, which validates exactly what will be committed.
6. Report what you changed, the choices you made on the owner's behalf and what remains uncertain.

## The graph

Each node is one file, `.specspec/<id>.md`, with YAML frontmatter (`id`, `type`, `parents`, `sources`) and a Markdown body. The *manifesto* is the root. A *requirement* states an outcome the product should achieve, a constraint it must respect or a choice of how, and names the parents it serves. An *implementation* node is a leaf under requirements: it explains how actual artifacts realize them and links them in `sources`.

```text
manifesto: Help a small team agree on a plan
  requirement: Make timing easy to read
    requirement: Show tasks on a weekday timeline
      implementation: Timeline rendering (sources: app.js)
```

Each indented line is a conclusion from the line above it, and that line is its intention; the two middle lines are both at once. No field stores this; it follows from the `parents` links. If a milestone list turns out to read better, the timeline node and its implementation are deleted and a new choice is added under "Make timing easy to read", which stays as it is.

To decide what belongs in a node, ask what should survive a change of approach. That outcome gets a node, and each choice with a real alternative gets its own node beneath it, so a choice can be replaced without erasing its outcome. Neither authorship nor specificity decides where a statement goes: a technology the owner must use is a constraint near the root, and one the owner merely suggested is a choice under the outcome it serves. Split a node when its parts could be replaced or reviewed separately; keep one coherent decision together.

A node may name several parents: every intention it serves or must respect. Keep the graph shortcut-free: a node serving both P and a descendant of P names only the descendant.

## Writing nodes

Node text describes the product as it is and as it ought to be now: requirements say what it ought to do, and implementation nodes say what exists, including its limits. A conclusion states the choice and how it serves its parents. Write positive, present-tense sentences about what the product does.

Git keeps the history: earlier versions stay in earlier commits, the reason for a change goes into the commit message, and a node that no longer applies is deleted. Avoid historic contrasting, about what changed and about what stayed the same: "the button is purple" is complete, while "the button is now purple instead of blue" and "the button remains purple" lean on an earlier version. Each sentence should make sense to a reader who knows only the current text.

Aim for an implementation-mature graph, precise enough that implementing it is close to compiling it: state observable behavior and every meaningful choice, and say in the node where a choice is deliberately left open. Every node in the graph is in force; there are no approval or confidence marks. The owner reviews where uncertainty and impact are highest, with passing checks and tests as evidence.

## Phases

The owner's request decides which phase applies.

### Owner planning

The owner may edit nodes directly. Routine step 1 finds those edits; work out what they mean for outcomes and choices before you do anything else.

### Tandem planning

The owner talks about what they want without yet asking for the graph or the product; you discuss it and leave the graph as it is. The owner's focus is breadth, the outcomes the product should have; yours is depth, the choices that achieve them, and breadth too where a gap is obvious. Separate what the owner wants from the choices they suggested, confirm or challenge those choices, and propose alternatives and your own conclusions. The owner leads: give a concise overview of your understanding, ready for correction, with guiding questions and your tentative answers, and concentrate on the choices that matter. Talk about the product rather than about nodes, with one exception: mention removals, splits and changes of existing nodes as soon as you consider them. The phase can take several rounds or be skipped.

### Agent planning

This phase starts when the owner asks you to create or change the graph ("draw the graph", "change the spec"). The request authorizes two commits. First commit the owner's uncommitted specification edits, if any, as `Owner specspec changes: <your understanding of them>`. Then work from the existing graph, its Git history, the owner's edits and the tandem rounds to make the graph implementation-mature: complete the depth that building needs, and fill breadth where the owner evidently left a gap for you. Commit it as `Agent specspec changes: <description>`. Run the staged check before each commit, and finish with a summary of changed outcomes, your choices, open questions and affected nodes.

### Implementation

This phase starts when the owner asks you to build or change the product, and it includes agent planning: first plan what you are asked to build, with the same two commits. Then keep graph and product in sync as you build: record each choice the graph still leaves to you as a requirement under the intention it serves, describe what you built in implementation nodes, and keep existing explanations and `sources` current. Removing nodes is the owner's decision. When nodes contradict each other, implement a simple, broad subset of the graph that is free of the contradiction, and report the conflict, the subset you chose and its consequences. When you see a way to improve the product, report the idea. You can offer to work either out as a graph on a separate branch.

## Commands

Install with `uv tool install specspec` (or `pipx install specspec`) and run commands inside the project, like Git. IDs such as `TZ971GA=` are written in full, including the final `=`. `add` prints the ID it creates.

```sh
specspec query ID --max-distance 1   # a node and its children
specspec add --parent PARENT_ID -m '# Title' -m 'Paragraph.'   # a requirement
specspec add --type implementation --parent REQUIREMENT_ID -m '# Realization'
specspec update ID --replace 'old passage' 'new passage'
specspec update ID --parent FIRST_ID --parent SECOND_ID   # replaces the parent list
specspec delete ID --dry-run
```

A bare `specspec query` prints the whole graph, so bound reads with `--max-distance`. `-m` values are literal Markdown paragraphs; long bodies can come from standard input instead.

Several add, update and delete steps can form one invocation. `--as name` names a new node and `--parent '$name'` links to it; `--dry-run` (preview), `--require-valid` (refuse an invalid result) and `--yes` apply to all steps. Replacing a choice and its implementation under their intention:

```sh
specspec delete CHOICE_ID IMPL_ID add --parent INTENTION_ID -m '# New choice' --require-valid
```

Deletion removes exactly the selected files: descendants keep their files and their now-missing parent references, so reconnect, rewrite or delete them deliberately. Deleting a node with uncommitted changes needs `--yes`.

Source links: `specspec sources capture IMPL_ID PATH --range 10:40 --mode expanding --staged` anchors a line range to the staged version of a file (stage the code first). `expanding` lets edits inside the range pass; `strict` reports them for review. A whole-file link is the one hand edit: a `- path: FILE` line under `sources:` in the node's frontmatter. When `check --sources` reports a link whose code changed, moved or disappeared, align the explanation and the code, stage the code, then run `specspec sources reanchor IMPL_ID --source N --staged`.

After an interrupted write, keep `.specspec/local/` (local state that Git ignores) and run `specspec recover`. Every command explains itself with `--help`.

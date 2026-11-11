# Working with a specspec graph

This project is developed with specspec, short for *specification spectrum*. Its specification is a graph of Markdown nodes in `.specspec/`, whose root states what the product is for. Every other node is a *conclusion* drawn from its parents, which are its *intentions*: it refines them, chooses a way to achieve them or explains what was built.

A specification worked out with a coding agent blends the outcomes the owner (the person you work for) wants with choices that were proposed and accepted along the way. Here each outcome and each meaningful choice is a node of its own, so a choice can be replaced while its outcome stays, and the owner can specify one branch in detail and delegate another. Record each choice you make as its own node under the intention it serves, where the owner can review and replace it.

## Routine

1. Check for owner input first: `git status`, `specspec diff` for specification changes since the last commit, the diffs of other files (including untracked ones), and `specspec spotlight show` for messages the owner attached to nodes. Uncommitted changes from an earlier agent session are your own unfinished work; ask when unsure whose a change is.
2. Find the nodes your task touches: `specspec query --max-distance 2` shows the top of the graph, and `specspec sources show` lists which implementation node links which file.
3. Before you change a node or the artifacts it describes, read it with its ancestors, which bind as much as the node itself: `specspec query ID --max-distance 0 --with-ancestors`.
4. Work in the phase the owner asked for (see Phases). You change the graph only in agent planning and implementation, with `specspec add`, `update` and `delete`.
5. After changing the graph or linked artifacts, run `specspec check --sources`. Before any commit, stage the complete change and run `specspec check --staged --sources --warnings-as-errors`.
6. Report what you changed, the choices you made on the owner's behalf and what remains uncertain. Whenever you discuss specific nodes, also spotlight them and say so: `specspec spotlight add ID... 'message'`.

## The graph

Each node is one file, `.specspec/<id>.md`, with YAML frontmatter (`id`, `type`, `parents`, `sources`) and a Markdown body. The *manifesto* is the root. A *requirement* states an outcome the product should achieve, a constraint it must respect or a choice of how, and names the parents it serves. An *implementation* node is a leaf under requirements: it explains how actual artifacts realize them and links them in `sources`.

```text
manifesto: Help a small team agree on a plan
  requirement: Make timing easy to read
    requirement: Show tasks on a weekday timeline
      implementation: Timeline rendering (sources: app.js)
```

Each indented line is a conclusion from the line above it, and that line is its intention. If a milestone list turns out to read better, the timeline node and its implementation are deleted and a new choice is added under "Make timing easy to read", which stays as it is.

To decide what belongs in a node, ask what should survive a change of approach. That outcome gets a node, and each choice with a real alternative gets its own node beneath it. A technology the owner must use is a constraint near the root, and one the owner merely suggested is a choice under the outcome it serves. Split a node when its parts could be replaced or reviewed separately; keep one decision together, such as a list of limits. An order of work, an option you did not choose, a topic that only groups other nodes and a rewording of the parent are not nodes.

An owner's sentence often names a way and leaves the outcome to you. Each becomes two nodes:

```text
owner: "a timeline, so everyone sees when things happen"
  requirement: Everyone sees when things happen
    requirement: Show tasks on a timeline
owner: "an SMS when the parcel ships"
  requirement: Customers know when their parcel ships
    requirement: Send an SMS when the parcel ships
owner: "the open tickets on the office TV"
  requirement: The team sees its open tickets at a glance
    requirement: Show the open tickets on the office TV
```

A node may name several parents: every intention it serves or must respect. Keep the graph shortcut-free: a node serving both P and a descendant of P names only the descendant.

## Writing nodes

Requirements say what the product ought to do, and implementation nodes say what exists, including its limits. A conclusion states the choice and how it serves its parents. Write positive, present-tense sentences about what the product does.

Git keeps the history, the reason for a change goes into the commit message, and a node that no longer applies is deleted. Avoid historic contrasting: "the button is purple" is complete, while "the button is now purple instead of blue" and "the button remains purple" lean on an earlier version. The time before the product and what the product is not stay out as well: "everyone sees the same plan" is complete, while "no more spreadsheets by e-mail" leans on the old way, and "the timeline shows Monday to Friday" is complete, while "the timeline does not show weekends" leans on something the product is not.

Aim for an implementation-mature graph, precise enough that implementing it is close to compiling it: state observable behavior and every meaningful choice, and say in the node where a choice is deliberately left open. Every node is in force; there are no approval or confidence marks.

## Phases

The owner's request decides which phase applies.

### Owner planning

The owner may edit nodes directly. Routine step 1 finds those edits.

### Structure review

This phase starts when routine step 1 finds nodes the owner edited. Hold each one against the rules in The graph and Writing nodes, tell the owner, node by node, what you would split, move or reword and why, and leave the graph as it is. Only what the owner accepts gets done: you apply it in agent planning, after their edits are committed as they wrote them. Everything else stays in the owner's words.

### Tandem planning

The owner talks about what they want without yet asking for the graph or the product; you discuss it and leave the graph as it is. Separate what the owner wants from the choices they suggested, confirm or challenge those choices, and propose alternatives and your own conclusions. The owner leads: give a concise overview of your understanding, with guiding questions and your tentative answers. Talk about the product rather than about nodes, with one exception: mention removals, splits and changes of existing nodes as soon as you consider them.

### Agent planning

This phase starts when the owner asks you to create or change the graph ("draw the graph", "change the spec"). The request authorizes two commits. First commit the owner's uncommitted specification edits, if any, as `Owner specspec changes: <your understanding of them>`. Then work from the existing graph, the owner's edits, the suggestions they accepted and the tandem rounds to make the graph implementation-mature. Commit it as `Agent specspec changes: <description>`. Run the staged check before each commit, and finish with a summary of changed outcomes, your choices, open questions and affected nodes.

### Implementation

This phase starts when the owner asks you to build or change the product, and it includes agent planning: first plan what you are asked to build, with the same two commits. Then keep graph and product in sync as you build: record each choice the graph still leaves to you as a requirement under the intention it serves, describe what you built in implementation nodes, and keep existing explanations and `sources` current. Removing nodes is the owner's decision. When nodes contradict each other, implement a simple, broad subset of the graph that is free of the contradiction, and report the conflict, the subset you chose and its consequences. When you see a way to improve the product, report the idea; you can offer to work it out as a graph on a separate branch.

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

A bare `specspec query` prints the whole graph, so bound reads with `--max-distance`.

Several add, update and delete steps can form one invocation. `--as name` names a new node and `--parent '$name'` links to it; `--dry-run` (preview), `--require-valid` (refuse an invalid result) and `--yes` apply to all steps. Replacing a choice and its implementation under their intention:

```sh
specspec delete CHOICE_ID IMPL_ID add --parent INTENTION_ID -m '# New choice' --require-valid
```

Deletion removes exactly the selected files: descendants keep their files and their now-missing parent references, so reconnect, rewrite or delete them deliberately.

Source links: `specspec sources capture IMPL_ID PATH --range 10:40 --mode expanding --staged` anchors a line range to the staged version of a file. A whole-file link is the one hand edit: a `- path: FILE` line under `sources:` in the node's frontmatter. When `check --sources` reports a link whose code changed, align the explanation and the code, stage the code, then run `specspec sources reanchor IMPL_ID --source N --staged`.

After an interrupted write, keep `.specspec/local/` and run `specspec recover`. Every command explains itself with `--help`.

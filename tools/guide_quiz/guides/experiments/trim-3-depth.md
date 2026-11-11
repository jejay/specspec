# Working with a specspec graph

This project is developed with specspec, short for *specification spectrum*. Its specification is a graph of Markdown nodes in `.specspec/`: the root states what the product is for, and every other node is a *conclusion* drawn from its parents, its *intentions*. Each outcome the owner (the person you work for) wants and each meaningful choice is a node of its own, so a choice can be replaced while its outcome stays. Many choices will be yours. Record each as its own node under the intention it serves, where the owner can review and replace it.

## Routine

1. Check for owner input first: `git status`, `specspec diff`, the diffs of other files and `specspec spotlight show`. Uncommitted changes from an earlier agent session are your own unfinished work; ask when unsure.
2. Find the nodes your task touches: `specspec query --max-distance 2` shows the top of the graph, `specspec sources show` which implementation node links which file.
3. Before you change a node or the artifacts it describes, read it with its ancestors, which bind as much as the node: `specspec query ID --max-distance 0 --with-ancestors`.
4. Work in the phase the owner asked for. You change the graph only in agent planning and implementation, with `specspec add`, `update` and `delete`.
5. After changes, run `specspec check --sources`. Before any commit, stage the complete change and run `specspec check --staged --sources --warnings-as-errors`.
6. Report what you changed, the choices you made for the owner and what remains uncertain, and spotlight the nodes you discuss: `specspec spotlight add ID... 'message'`.

## The graph

Each node is one file, `.specspec/<id>.md`, with YAML frontmatter (`id`, `type`, `parents`, `sources`) and a Markdown body. The *manifesto* is the root. A *requirement* states an outcome, a constraint or a choice of how, and names the parents it serves. An *implementation* node is a leaf under requirements: it explains how actual artifacts realize them and links them in `sources`.

```text
manifesto: Help a small team agree on a plan
  requirement: Make timing easy to read
    requirement: Show tasks on a weekday timeline
      implementation: Timeline rendering (sources: app.js)
```

If a milestone list reads better, the timeline node and its implementation are deleted and a new choice is added under "Make timing easy to read", which stays as it is.

Ask what should survive a change of approach: that outcome gets a node, and each choice with a real alternative gets its own node beneath it. A technology the owner must use is a constraint near the root; one they merely suggested is a choice under the outcome it serves. Keep one decision together, such as a list of limits. An order of work, an option you did not choose, a topic that only groups other nodes and a rewording of the parent are not nodes.

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

Requirements say what the product ought to do; implementation nodes say what exists, including its limits. Write positive, present-tense sentences about what the product does. History stays in Git: "the button is purple" is complete, while "the button is now purple instead of blue" leans on an earlier version, "no more spreadsheets by e-mail" on the old way of working, and "the timeline does not show weekends" on something the product is not.

Aim for an implementation-mature graph, precise enough that implementing it is close to compiling it: state observable behavior and every meaningful choice, and say in the node where a choice is deliberately left open. Every node is in force; there are no approval or confidence marks.

## Phases

- Owner planning: the owner may edit nodes directly; routine step 1 finds those edits.
- Structure review: when you find nodes the owner edited, hold them against the rules above, tell the owner what you would split, move or reword and why, and leave the graph as it is. What the owner accepts, you apply in agent planning, after their edits are committed as they wrote them. Everything else stays in the owner's words.
- Tandem planning: the owner talks about what they want without asking for the graph or the product. Discuss it and leave the graph as it is. Separate what the owner wants from the choices they suggested, challenge those choices and propose your own. Mention removals, splits and changes of existing nodes as soon as you consider them.
- Agent planning starts when the owner asks you to create or change the graph ("draw the graph", "change the spec"). The request authorizes two commits: first the owner's uncommitted specification edits as `Owner specspec changes: <your understanding of them>`, then your own work as `Agent specspec changes: <description>`. Make the graph implementation-mature: complete the depth that building needs, and fill breadth where the owner evidently left a gap for you. Finish with a summary of changed outcomes, your choices, open questions and affected nodes.
- Implementation starts when the owner asks you to build or change the product, and it begins with agent planning. Keep graph and product in sync: record each choice the graph leaves to you as a requirement, describe what you built in implementation nodes, and keep `sources` current. Removing nodes is the owner's decision. When nodes contradict each other, implement a simple, broad subset that is free of the contradiction and report it. Report ideas for improving the product.

## Commands

IDs such as `TZ971GA=` are written in full, including the final `=`. `add` prints the ID it creates.

```sh
specspec query ID --max-distance 1   # a node and its children
specspec add --parent PARENT_ID -m '# Title' -m 'Paragraph.'   # a requirement
specspec add --type implementation --parent REQUIREMENT_ID -m '# Realization'
specspec update ID --replace 'old passage' 'new passage'
specspec update ID --parent FIRST_ID --parent SECOND_ID   # replaces the parent list
specspec delete CHOICE_ID IMPL_ID add --parent INTENTION_ID -m '# New choice' --require-valid
```

A bare `specspec query` prints the whole graph, so bound reads with `--max-distance`. Steps can form one invocation; `--as name` names a new node and `--parent '$name'` links to it. Deletion removes exactly the selected files: descendants keep their now-missing parent references, so reconnect, rewrite or delete them deliberately.

A whole-file source link is a `- path: FILE` line under `sources:` in the node's frontmatter. When `check --sources` reports a link whose code changed, align the explanation and the code, stage the code, then run `specspec sources reanchor IMPL_ID --source N --staged`. After an interrupted write, keep `.specspec/local/` and run `specspec recover`. Every command explains itself with `--help`.

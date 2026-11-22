# Working with a specspec graph

This project is developed with specspec, short for *specification spectrum*. Its specification is a graph of Markdown nodes in `.specspec/`, whose root states what the product is for. Every other node is a *conclusion* drawn from its parents, which are its *intentions*: it refines them, chooses a way to achieve them or explains what was built. The same node is in turn an intention for the nodes beneath it. From the root outward, the nodes run from what the owner (the person you work for) intends, through ever more concrete conclusions, to the actual files. That range is the spectrum.

The graph exists because a specification worked out with a coding agent loses track of what was concluded from what. The owner's intentions and the conclusions that were proposed and accepted along the way end up in one text, and a few rounds later it is hard to tell which details are essential. Here every conclusion is a node of its own beneath the intentions it was drawn from. A conclusion is one valid conclusion among others: it rests on reasoning, stated or not, and may be replaced at any time. Replacing a node leaves everything above it in force and puts everything beneath it up for review, so the owner can change their mind at any depth, specify one branch in detail and delegate another. Many conclusions will be yours to draw. Record each as its own node under the intention it serves, where the owner can review and replace it.

Whatever the owner says or writes, first tell intention from conclusion: what do they intend, and which conclusions have they already drawn from it? Their wording rarely says which is which, and how firmly a statement holds is in the owner's head, not in the graph. For a Python library the language is part of the intention; for an app whose owner has no preference it is a conclusion far down, and often yours. Infer what the owner holds as intention from what they say, the reasons they give and the product. Say how you read them, and ask where you cannot tell and a wrong reading would cost much.

## Routine

1. Check for owner input first: `git status`, `specspec diff` for specification changes since the last commit, the diffs of other files (including untracked ones), and `specspec spotlight show` for messages the owner attached to nodes. The owner may also have committed edits themselves: look in `git log` for the newest commit titled `Agent specspec changes:`, and `specspec diff COMMIT` shows every specification change since it. Uncommitted changes from an earlier agent session are your own unfinished work; ask when unsure whose a change is.
2. Find the nodes your task touches: `specspec query --max-distance 2` shows the top of the graph, and `specspec sources show` lists which implementation node links which file.
3. Before you change a node or the artifacts it describes, read it with its ancestors: `specspec query ID --max-distance 0 --with-ancestors`. Its ancestors are the reasons it exists, and they bind as much as the node itself.
4. Work in the phase the owner asked for (see Phases). You change the graph only in agent planning and implementation, with `specspec add`, `update` and `delete`.
5. After changing the graph or linked artifacts, run `specspec check --sources`. Before any commit, stage the complete change and run `specspec check --staged --sources --warnings-as-errors`, which validates exactly what will be committed.
6. Report what you changed, the conclusions you drew on the owner's behalf and what remains uncertain. Whenever you discuss specific nodes, also spotlight them and say so: `specspec spotlight add ID... 'message'` shows them in the owner's graph editor.

## The graph

Each node is one file, `.specspec/<id>.md`, with YAML frontmatter (`id`, `type`, `parents`, `sources`) and a Markdown body. The *manifesto* is the root and holds intentions only. A *requirement* states what the product should do or respect and names the parents it is concluded from. An *implementation* node is a leaf under requirements: it explains how actual artifacts realize them and links them in `sources`.

```text
manifesto: Help a small team agree on a plan
  requirement: Make timing easy to read
    requirement: Show tasks on a weekday timeline
      implementation: Timeline rendering (sources: app.js)
```

Each indented line is a conclusion from the line above it, and that line is its intention; the two middle lines are both at once. No field stores this; it follows from the `parents` links. If a milestone list turns out to read better, the timeline node and its implementation are deleted and a new conclusion is added under "Make timing easy to read", which stays as it is. If timing itself stops mattering, "Make timing easy to read" is replaced the same way beneath the manifesto, and what hung beneath it is looked at again.

To place a statement, ask what it is for. The answer is its intention and goes above it: when the graph does not hold that intention yet, word it and give it a node. An intention's text is what should survive a change of approach, so it names no way of achieving it, and a conclusion can be replaced without erasing its intention. Then ask what follows from the statement that building needs and nobody has said: those conclusions are yours to draw, each in a node of its own beneath it. Neither authorship nor specificity decides where a statement goes: a technology the owner must use is an intention near the root, and one the owner merely suggested is a conclusion under the intention it serves. Split a node when its parts could be replaced or reviewed separately; keep one coherent conclusion together, such as a list of limits. An order of work, a conclusion you considered and set aside, a topic that only groups other nodes and a rewording of the parent are not nodes.

An owner's sentence often states a conclusion and leaves its intention to you, or gives both in one breath. Each becomes two nodes:

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

Node text describes the product as it is and as it ought to be now: requirements say what it ought to do, and implementation nodes say what exists, including its limits. A conclusion says what the product does and how that serves its intentions. Write positive, present-tense sentences about what the product does.

Git keeps the history: earlier versions stay in earlier commits, the reason for a change goes into the commit message, and a node that no longer applies is deleted. Avoid historic contrasting, about what changed and about what stayed the same: "the button is purple" is complete, while "the button is now purple instead of blue" and "the button remains purple" lean on an earlier version. Each sentence should make sense to a reader who knows only the current text.

The time before the product and what the product is not stay out as well. What goes wrong today tells you an intention, and the node says what the product does: "everyone sees the same plan" is complete, while "no more spreadsheets by e-mail" leans on the old way, and so does "nobody works from an old copy". "The timeline shows Monday to Friday" is complete, while "the timeline does not show weekends" leans on something the product is not.

Aim for an implementation-mature graph, precise enough that implementing it is close to compiling it: state observable behavior and every conclusion that building needs, and say in the node where one is deliberately left open. Every node in the graph is in force until it is replaced; there are no approval or confidence marks. The owner reviews where uncertainty and impact are highest, with passing checks and tests as evidence.

## Phases

The owner's request decides which phase applies.

### Owner planning

The owner may edit nodes directly and may commit them. Routine step 1 finds those edits; work out what they mean before you do anything else: which intention each edit states or changes, and which conclusions beneath it are up for review.

### Structure review

Every `Agent specspec changes:` commit seals the graph beneath it, and a graph without one is open as a whole. What the owner changed by hand since the newest one is open, whether they committed it or not, and this phase starts when routine step 1 finds such changes. Commit the uncommitted ones first, exactly as the owner wrote them, as `Owner specspec changes: <your understanding of them>`; this commit keeps the owner's words on record and seals nothing.

Then read each open node with its ancestors and hold it against the rules in The graph and Writing nodes. An open manifesto is read too: it holds intentions only, so a conclusion in its wording, such as a layout or a technology that is not a given, belongs in a node beneath it. Tell the owner what you would split, merge, move or reword and why, and leave the graph as it is. Propose what makes the best graph, and keep to points that matter. What the owner accepts, you commit as `Agent specspec changes: <description>`; everything else stays in the owner's words.

Sealed nodes stand as they are. Change one where a request cannot be recorded well without it, and name it in your summary; a request to review or restructure opens whatever it names. Sealed nodes that your request does not touch get no remark about their structure or wording. An obvious flaw in a sealed node you are working at may get one line in your summary, once.

### Tandem planning

The owner talks about what they want without yet asking for the graph or the product; you discuss it and leave the graph as it is. Tell the owner's intentions from the conclusions they have already drawn, and say how you read each. Hold every conclusion against its intention: object where one does not fit, and propose your own. Mention removals, splits and changes of existing nodes as soon as you consider them. Close with guiding questions and your tentative answer to each.

### Agent planning

This phase starts when the owner asks you to create or change the graph ("draw the graph", "change the spec"). Open edits of the owner get their structure review along the way: commit them as written, plan what the owner asked for and put your suggestions about their edits, and about an open manifesto, into your summary. Work from the existing graph, its Git history, the owner's edits, the suggestions they accepted and the tandem rounds to make the graph implementation-mature: complete the depth that building needs, and fill breadth where the owner evidently left a gap for you. Commit your planning on its own as `Agent specspec changes: <description>`. Run the staged check before each commit, and finish with a summary: the intentions you read into the owner's words, your own conclusions, open questions and affected nodes.

### Implementation

This phase starts when the owner asks you to build or change the product, and it includes agent planning: first plan what you are asked to build and commit that planning. Then keep graph and product in sync as you build: record each conclusion the graph still leaves to you as a requirement under the intention it serves, describe what you built in implementation nodes, and keep existing explanations and `sources` current. Commit every change to requirement nodes on its own as `Agent specspec changes: <description>`, also one you record in the middle of building; code and implementation nodes go into the project's ordinary commits. Removing nodes is for the owner to decide. When nodes contradict each other, implement a simple, broad subset of the graph that is free of the contradiction, and report the conflict, the subset you chose and its consequences. When you see a way to improve the product, report the idea. You can offer to work either out as a graph on a separate branch.

## Commands

Install with `uv tool install specspec` (or `pipx install specspec`) and run commands inside the project, like Git. IDs such as `TZ971GA=` are written in full, including the final `=`. `add` prints the ID it creates.

```sh
specspec query ID --max-distance 1   # a node and its children
specspec add --parent PARENT_ID -m '# Title' -m 'Paragraph.'   # a requirement
specspec add --type implementation --parent REQUIREMENT_ID -m '# Realization'
specspec update ID --replace 'old passage' 'new passage'
specspec update ID --parent FIRST_ID --parent SECOND_ID   # replaces the parent list
specspec delete CONCLUSION_ID IMPL_ID add --parent INTENTION_ID -m '# New conclusion' --require-valid
```

A bare `specspec query` prints the whole graph, so bound reads with `--max-distance`. Steps can form one invocation; `--as name` names a new node and `--parent '$name'` links to it. Deletion removes exactly the selected files: descendants keep their now-missing parent references, so reconnect, rewrite or delete them deliberately.

A whole-file source link is a `- path: FILE` line under `sources:` in the node's frontmatter. When `check --sources` reports a link whose code changed, align the explanation and the code, stage the code, then run `specspec sources reanchor IMPL_ID --source N --staged`. After an interrupted write, keep `.specspec/local/` and run `specspec recover`. Every command explains itself with `--help`.

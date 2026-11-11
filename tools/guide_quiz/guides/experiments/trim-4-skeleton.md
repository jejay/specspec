# Working with a specspec graph

The specification of this project is a specspec graph (*specification spectrum*) of Markdown nodes in `.specspec/`. The root states what the product is for; every other node is a conclusion drawn from its parents, its intentions. Each outcome the owner wants and each choice is a node of its own, so a choice can be replaced while its outcome stays.

## Routine

1. Check for owner input: `git status`, `specspec diff`, `specspec spotlight show`.
2. Find your nodes: `specspec query --max-distance 2`, `specspec sources show`.
3. Read a node with its ancestors before changing it: `specspec query ID --max-distance 0 --with-ancestors`.
4. Change the graph only in agent planning and implementation, with `specspec add`, `update` and `delete`.
5. Run `specspec check --sources` after changes and `specspec check --staged --sources --warnings-as-errors` before a commit.
6. Report your changes, your own choices and what is uncertain; spotlight discussed nodes with `specspec spotlight add ID... 'message'`.

## The graph

A node is a file `.specspec/<id>.md` with frontmatter (`id`, `type`, `parents`, `sources`) and a Markdown body. Types: one *manifesto* (the root), *requirement* (an outcome, a constraint or a choice), *implementation* (a leaf that explains existing files and links them in `sources`).

```text
manifesto: Help a small team agree on a plan
  requirement: Make timing easy to read
    requirement: Show tasks on a weekday timeline
      implementation: Timeline rendering (sources: app.js)
owner: "an SMS when the parcel ships"
  requirement: Customers know when their parcel ships
    requirement: Send an SMS when the parcel ships
```

- An outcome gets a node; each way of achieving it gets a node beneath it, also when the owner named the way.
- A technology the owner must use is a constraint near the root.
- One decision is one node; a list of limits stays together.
- A node names every intention it serves or must respect as a parent, and never both a node and its ancestor.
- An order of work, an option not chosen, a topic that only groups nodes and a rewording of the parent are not nodes.
- Node text says what the product does, in positive present tense, without history ("now ... instead of ..."), without the old way of working and without what the product is not.
- Every node is in force.

## Phases

- Structure review: when the owner edited nodes, tell them what you would split, move or reword, and leave the graph as it is. Apply only what they accept.
- Tandem planning: the owner talks about what they want. Discuss it and leave the graph as it is.
- Agent planning ("draw the graph", "change the spec"): commit the owner's edits as `Owner specspec changes: ...`, then your own as `Agent specspec changes: ...`, and summarize.
- Implementation ("build ..."): plan first, then build and keep graph and product in sync. Removing nodes is the owner's decision. Report contradictions and ideas.

## Commands

```sh
specspec add --parent PARENT_ID -m '# Title' -m 'Paragraph.'
specspec add --type implementation --parent REQUIREMENT_ID -m '# Realization'
specspec update ID --replace 'old passage' 'new passage'
specspec update ID --parent FIRST_ID --parent SECOND_ID   # replaces the parent list
specspec delete CHOICE_ID IMPL_ID add --parent INTENTION_ID -m '# New choice' --require-valid
specspec sources reanchor IMPL_ID --source N --staged
specspec recover
```

IDs are written in full, including the final `=`. Deletion removes exactly the selected files. Every command explains itself with `--help`.

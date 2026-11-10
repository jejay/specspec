<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/jejay/specspec/main/branding/specspec-logo-tagline-dark.png">
  <img src="https://raw.githubusercontent.com/jejay/specspec/main/branding/specspec-logo-tagline-light.png" alt="specspec — Engineering is on the spectrum now" width="640">
</picture>

specspec connects your intentions to revisable decisions and to the code that realizes
them, so you can choose how much to direct or delegate at every step. The specification
is a graph of Markdown files in your Git repository. You work on it in a visual graph
editor or the terminal, and your coding agent uses the same CLI.

The name is short for *specification spectrum*.

## Why

When you build with a coding agent, much of the specification gets written in
conversation. You describe a goal, the agent proposes a way to reach it, you agree,
and it builds. A few rounds later, what you wanted and what the agent suggested have
merged into one plan. Some details are there because you need them, others because
they were the first idea that worked, and the plan reads the same either way.

That matters once you want to try something else. With an agent, rebuilding the data
model or the UI takes minutes. The hard part is knowing what the old one was for, so
that the new one keeps it. specspec keeps that knowledge in the repository, next to
the code.

## The specification spectrum

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/jejay/specspec/main/docs/images/spectrum-dark.svg">
  <img src="https://raw.githubusercontent.com/jejay/specspec/main/docs/images/spectrum-light.svg" alt="A specspec graph for a planning app. The manifesto, Help a small team agree on a plan, leads to two intentions, three choices that serve them and three implementation nodes that point to source lines. A color band underneath runs from intention to conclusion.">
</picture>

Every node is a short Markdown file in `.specspec/`. The root is the *manifesto*: what
the project is for. Every other node names the parents it serves, either refining them
or choosing a way to achieve them. *Implementation* nodes at the outer edge explain how
the code realizes a requirement and link to the files and line ranges involved.

Near the manifesto, nodes are mostly intention: what you want and why. Further out,
they are mostly conclusion: how it gets done. A node's place on that spectrum follows
from its position in the graph. A requirement is a conclusion for its parents and an
intention for its children.

One choice can serve several intentions, which makes the graph a directed acyclic graph
rather than a tree. In the file, that is simply a second parent:

```markdown
---
id: OHYE-rI=
type: requirement
parents:
- rrvyriU=
- ABOH2aU=
---
# Highlight what moved since the last version

Compare the plan with the previous commit and mark changed dates.
```

Giving each intention and each choice its own node is what keeps solutions revisable.
"Show tasks on a weekday timeline" is one way to make timing easy to read. If a list of
milestones works better, you replace that branch. The intention above it stays, and the
new choice is written to serve it.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/jejay/specspec/main/docs/images/revise-dark.svg">
  <img src="https://raw.githubusercontent.com/jejay/specspec/main/docs/images/revise-light.svg" alt="Replacing a conclusion. The intention Make timing easy to read is unchanged. The weekday timeline and its implementation are marked D for deleted and kept in Git history; a milestone list and its implementation are marked A for added.">
</picture>

## The other spectrum

The tagline, *Engineering is on the spectrum now*, refers to a second range: from
hands-on engineering, where you make every decision yourself, to vibe coding, where the
agent makes them for you. Most projects need both, in different places, and specspec
lets you choose per branch.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/jejay/specspec/main/docs/images/direct-dark.svg">
  <img src="https://raw.githubusercontent.com/jejay/specspec/main/docs/images/direct-light.svg" alt="The same planning graph with a shaded area for your decisions. You decided the timeline down to the code, chose to highlight moved dates, and stated only the goal for proposing changes. The remaining nodes were concluded by the agent.">
</picture>

In this example you designed the timeline yourself, down to the code. You asked for
moved dates to be highlighted and left the implementation to the agent. For proposing
changes, you stated only the goal, and the agent chose a JSON file in the repository
and wrote its validation. The agent's conclusions are nodes like any other: you can
read them now and keep or replace them later.

## Working with an agent

specspec works with the coding agent you already use, as long as it can run shell
commands. `specspec init` writes an `AGENTS.md` that explains the graph and this
workflow to it:

1. You describe what you want and cover the breadth. The agent works out the depth:
   it separates your intentions from the solutions you proposed, questions choices
   that look weak and suggests its own. The graph stays as it is while you talk.
   Skip this step when the request is clear.
2. When you ask for it, the agent writes the graph with `specspec add`, `update` and
   `delete`, building on any edits you made yourself, and reports its choices and open
   questions. If you want commits, your edits and its changes go into separate ones.
3. You review. The graph editor marks nodes added, changed or deleted since the last
   commit, and `specspec diff` shows the full text. Edit any node directly, or select
   a few nodes and leave the agent a message about them (a *spotlight*).
4. The agent implements. Before it changes code, it reads the node and every ancestor
   that justifies it. Where the graph leaves room for interpretation, it adds deeper
   conclusions and implementation nodes linked to the code. Scope changes come back to
   you; when it finds a contradiction, it builds a consistent part and reports the rest.
5. When you change your mind, you change the intention or replace the choice. The
   graph describes the current plan; Git keeps the earlier ones and the reasons they
   changed.

The goal is a graph precise enough that implementing it comes close to compiling it,
with little left for the agent to guess. How closely you review on the way is up to
you. Look hard where uncertainty and impact are high, and decide when the graph is clear
enough to be worth an implementation attempt. Each attempt is evidence for the next
revision. The [agent guide](https://github.com/jejay/specspec/blob/main/src/specspec/templates/AGENTS.md) is the file `init` adds.

## Try it

The CLI needs Python 3.11+ and Git. Install it from
[PyPI](https://pypi.org/project/specspec/):

```sh
uv tool install specspec    # or: pipx install specspec
```

In a project directory, create the manifesto. `init` sets up a Git repository if there
is none and writes `AGENTS.md`, or appends to the one you have:

```sh
specspec init -m "# Help a small team agree on a plan" -m "Everyone sees the same dates and why they moved."
```

It prints the manifesto's ID, such as `TZ971GA=`. IDs end in `=`; copy them whole.
The everyday commands:

```sh
specspec query --max-distance 2                      # the top of the graph
specspec query ID --max-distance 0 --with-ancestors  # one node and everything that justifies it
specspec add --parent ID -m "# Make timing easy to read" -m "Everyone sees when each task happens."
specspec update ID --replace "old wording" "new wording"
specspec delete ID
specspec diff                                        # changes since the last commit
specspec check                                       # structural validation
```

Every command has `--help` with examples. If `specspec` isn't found, run
`uv tool update-shell` (or `pipx ensurepath`) and open a new terminal; upgrade with
`uv tool upgrade specspec`.

### Graph editors

The VS Code extension and the desktop app draw the graph on a zoomable canvas, open
each node in an editor and compare any two revisions. For now you build them from this
repository, which needs Node 22.12+ and npm 10+. Both run the `specspec` command you
installed.

```sh
git clone https://github.com/jejay/specspec.git
cd specspec
npm ci
npm run package:vscode    # then: code --install-extension dist/specspec-vscode-0.0.1.vsix
npm run desktop           # or start the desktop app from source
```

In VS Code, run **specspec: Open Graph** from the Command Palette. The desktop app runs
on Windows and Linux; on macOS, use VS Code. The
[editor guide](https://github.com/jejay/specspec/blob/main/vscode/README.md) covers the canvas, reviewing changes,
spotlights and settings.

## A planner that changed its mind

[`example/gantt`](https://github.com/jejay/specspec/blob/main/example/gantt/README.md)
is a small planning app built with specspec, with its own Git history. It changed
direction twice: from a portfolio tool for business projects, to a personal planner
with hand-picked dates, to a workshop planner that forecasts finish dates. Each
redirect deleted the conclusions that no longer applied and kept the intentions that
still did. From this repository, with the CLI installed:

```sh
python example/gantt/history/checkout.py    # clones it to ~/Projects/specspec-examples/gantt
```

Open the clone in either editor and compare `stage/01-code` with `stage/02-spec`, or
run `specspec diff stage/01-code stage/02-spec` inside it.

## Status

specspec 0.0.1 is the first public release. The CLI is on PyPI; the editors are built
locally. Expect rough edges and changing commands.

Everything runs on your machine. The graph is Markdown in your repository, and you
stage and commit it like any other file. `specspec check` confirms that the graph is
well formed: one manifesto, every node reachable from it, no cycles. Whether the
product does what the nodes describe is for you, your tests and your agent to judge.
Implementation nodes help by pointing at the exact code, and
`specspec check --sources` flags linked code that has changed or disappeared since it
was linked.

specspec is developed with specspec. Its own graph is in
[`.specspec/`](https://github.com/jejay/specspec/tree/main/.specspec), and
[CONTRIBUTING](https://github.com/jejay/specspec/blob/main/CONTRIBUTING.md) explains how to work on it.

## More

- [Agent guide](https://github.com/jejay/specspec/blob/main/src/specspec/templates/AGENTS.md): the routine and rules your agent follows
- [Editor guide](https://github.com/jejay/specspec/blob/main/vscode/README.md): the VS Code extension and the desktop app
- [Contributing](https://github.com/jejay/specspec/blob/main/CONTRIBUTING.md): development setup, checks and releases
- [Changelog](https://github.com/jejay/specspec/blob/main/CHANGELOG.md)

specspec is [MIT licensed](https://github.com/jejay/specspec/blob/main/LICENSE).

# Working on specspec

## Project specification and review

The active specification is the tool-managed graph in `.specspec/`. Read
`docs/own-spec.md` for entry points, current choices, and withdrawn design history.
`INTENTION_SPEC.md` is the user's original source; `CONCLUSION_SPEC.md` records
technical conclusions. The graph also records the user's later corrections.

Use the installed CLI, or `python -m specspec` in the development environment:

```sh
python -m specspec query --max-distance 2
python -m specspec query <node-id> --max-distance 0 --with-ancestors
python -m specspec query <node-id>
python -m specspec diff
```

Inspect owner changes with Git status and full specification/code diffs. Query's
change hints are an orientation aid; `specspec diff` supplies canonical-file hunks
and `git diff` supplies code patches. Read untracked files explicitly. Use `--json`
when processing structured results; ordinary readable query output is complete.

Before changing code, read the relevant node and its ancestors. Use
`query <node-id> --max-distance 0 --with-ancestors` for a focused complete reading,
or add `--with-ancestors` to a larger selected subgraph. Completion follows every
parent path after metric selection; added ancestors consume no match quota. Skip
redundant reads only when those complete bindings have already been read. CLI reads
saved files, not unsaved editor buffers. Distinguish core
intentions from revisable conclusions by their relationships and explanations,
not proposed/accepted statuses. Review is risk-proportionate: earlier intentions
will often receive more attention, but depth is not a confidence score or a review
quota. When the user considers an implementation attempt worth its uncertainty and
token cost, there is no additional per-node approval ceremony before proceeding.

Keep conclusions revisable. Working code and passing tests are evidence, not proof
of correctness or a reason to silently rewrite the user's intentions. Surface
material uncertainty and conflicts rather than manufacturing agreement.

## Release workspace and generated guides

This checkout is a private npm workspace with one root `package-lock.json`.
Run `npm ci` at the root; CLI users normally install from PyPI with
`uv tool install specspec` or `pipx install specspec`. See `CONTRIBUTING.md` and `docs/releasing.md` for root build,
VSIX, portable desktop and artifact-check commands. Builds do not publish or install
into an owner's editor. Only separate explicit requests authorize release tags or publication.

The generic guide created by `init` is `src/specspec/templates/AGENTS.md`, adapted
from the owner drafting workspace and current tool contracts. Keep it generic and
validate wheel/sdist resources, exact selected deletion, ID-only `.specspec/` paths,
replacement defaults and explicit Git ownership. Init requires Git, initializes a
repository when needed, and creates or appends the template after exact existing
root instruction bytes. Preserve external edits through byte-checked recovery;
Git metadata stays outside graph rollback. Runtime state lives in `.specspec/local/`. Repository-specific
maintenance guidance remains here rather than being copied into every product.

## Changes

- Use `add`, `update`, and `delete` for ordinary canonical graph changes
  in this checkout. The product permits manual Markdown edits, but CLI/UI editing
  remains recommended. Current storage/protocol has no node hashes, fingerprints, or `--expect`; source blob IDs
  are Git content addresses, not node edit gates.
  The authorized compact-ID conversion is a one-time tool-managed migration,
  not a permanent compatibility command.
- Record a separate conclusion when a change introduces a meaningful choice.
  Do not rewrite its parent intention to make a chosen implementation inevitable.
- Do not introduce approval statuses, acceptance scores, or parent-review gates.
  Git differences communicate newness and change relative to the selected base.
- Withdraw by physically deleting node files; explain why in the Git commit.
  No retired flag or retire/restore workflow. Managed `delete` removes exactly the
  selected files and warns about uncommitted selected nodes before unlinking.
  Survivors retain missing-parent declarations. Inspect with `query --issues
  --with-ancestors` and `diff --with-context`; resolve deliberately with ordinary
  edits or combined add/update/delete steps. Edits can save graph-invalid
  intermediates; `--require-valid`
  checks the whole final candidate before writes. `check` stays strict. Never
  reparent or delete the manifesto. Default workspace compares to HEAD; D remains visible through staging
  and vanishes after commit. See `docs/deletion.md`.
- Keep implementation explanations and `sources` references current when code
  or verification changes. Source symbols remain descriptive. Blob/range locations are resolved through
  the shared backend; see `docs/source-regions.md`.
- Present specification changes, code changes, and affected nodes together.
- Account for earlier assistant-authored work as unfinished work, not somebody
  else's edits. Before reporting completion, explicitly account for remaining
  changes and finish authorized coherent spec/code slices with exact-index checks.
- Never silently stage files, create commits, or install/replace local Git hooks.

## Checks

```sh
python -m specspec check --warnings-as-errors
python -m ruff check .
python -m ruff format --check .
python -m pytest
npm --prefix graph-ui-common test
npm --prefix vscode test
npm --prefix electron test
```

Use `python -m specspec diff <current-scheme-ref> --json` for a review report
when the baseline uses the current schema. Before an explicitly authorized commit,
stage the complete intended graph change and run
`python -m specspec check --staged --sources --warnings-as-errors` against that exact
index; working-tree validation cannot substitute for staged validation.

Maintain only the current schema: current node format requires a shortcut-free rooted DAG.
No direct parent may already be an indirect parent. Review ripple effects against
both old and new graphs; related Markdown changes remain deliberate. See
`docs/graph-structure.md`. Use padded Base64url IDs over five random bytes,
including the final `=`, and `<id>.md` filenames. Do not retain overwritten
schemas, UUID readers, old metadata normalization or permanent migration commands.

This repository's own graph is self-referencing design documentation. Validate
its working graph and current source references, but do not require Git tooling
to work against its obsolete historical schemas. Rejected older revisions are
expected. Use the independent, rewritten current-schema Gantt history in
`example/gantt/history/gantt.bundle` for serious Git/temporal, host and application
integration tests. `example/gantt` is a tracked fixture snapshot, NOT a Git workspace;
Git there finds this repository. Run `python example/gantt/history/checkout.py` to
create `~/Projects/specspec-examples/gantt` for manual UI comparisons, or give a new
external destination for disposable tests. Do not install nested Git metadata.

EVERY node-schema change requires rewriting the ENTIRE maintained history of Gantt
and additional examples as if all revisions had always used today's specspec.
Refresh all retained refs, earlier/deleted nodes, actual receipts, commit ledgers, bundle
and tracked snapshot together; validate every revision with current tools. Updating
only HEAD or retaining old readers is not a solution. See
`example/gantt/history/WALKTHROUGH.md`. Preserve local experiments before explicitly
recreating stale clones; never reset them silently or rewrite unrelated specspec
history. Plausible graph emergence/revision is sufficient; fabricated AI dialogue
is not required. Focused unit tests may use smaller independent current-schema graphs.

If an edit is interrupted, retain `.specspec/local/` and run `recover`. Remove a
stale lock with `recover --force-lock` only after confirming no writer is running.

Part of this project is to work out a "specspec AGENTS.md" for specspec-driven development. The goal is to replace this whole AGENTS.md with the following text (or to work out a version of this text that will take this place). To keep the flexibility we need to accept that we cannot just do that, for example reliance on git history will break if we develop on breaking changes. Hence we need to approach/converge to the principles described in the following text: 

# PRELIMINARY SPECSPEC AGENTS.MD

# Intention-Conclusion Specification-Spectrum-Driven Development

A specification spectrum (specspec) graph documents and specifies the spectrum of the owner's intent to the the agent's conclusions for the development of a product. The intention-conclusion spectrum is represented as a directed acyclic graph of requirements, in which a parent-child connection stands for an intention-conclusion relationship. The root parent node, the manifesto, contains the core goal of the product. At the opposite end, leaf nodes can state conclusions about implementation details.

A specspec graph records what "is" and what "ought to be" at a certain point in time using positive language. Negative language to contrast what "is not", "ought not to be" or "was" is avoided. Historic contrasting ("this button was blue but now it is purple") is avoided, the history is managed via git and specspec's git aware tools. A perfectly implementation-mature specspec graph aims at enabling metaphorical compiler-level determinism once it is implemented by an agent.


## Phases of Specification-Spectrum Driven Development

### Owner Planning

The owner can optionally directly manually modify the specspec. The agent needs to check whether the owner modified the specspec before any action.
 

### Tandem Planning

The owner tells the agent what they want or the agent infers it from the existing manual specspec changes. The agent tries to separate the owner's intention from the owner's own conclusions. The agent tries to understand and learn about the owner's intention and conclusions. The agent challenges and either validates the conclusions or proposes alternative conclusions. The agent proposes and discusses its own additional conclusions.

In tandem planning the owner's focus is on breadth and the agent's focus is on depth. The agent can also focus on breadth either when asked explicitly or implicitly when the missing breadth is obvious.

The agent never steers the conversation, instead it gives the owner an overview of its understanding of the owner's intention, of its critique, conclusions, etc, ready to be corrected. It can offer guidance questions together with its own answers. The agent focuses on the most important issues and leaves out less controversial conclusions that would bloat the conversation.

The agent never discusses the planned addition of nodes to the specspec graph mid tandem planning. Contrary, the agent needs to discuss potential removals, split-ups and modifications of nodes immediately.

Tandem planning can have arbitrary number of rounds and also be skipped. In tandem planning the agent guides the owner and gathers information, understanding and approval; but in tandem planning the agent does not manipulate the specspec.


### Agent Planning

Agent planning phase is entered once the user requests the agent to manipulate the specspec (e.g. "draw the graph", "change the spec"). The goal of the phase is for the agent to create a perfectly implementation-mature specspec. If available the agent uses the pre-existing specspec, the historical context and the understanding and approvals from the tandem planning phase. If there was no tandem phase, the agent tries to infer the owner's intention and conclusions from the specspec git history and uncommitted workbench state. The agent commits the uncommitted manual specspec changes by the owner as "Owner specspec changes: [intention/conclusion agent understanding description]" before changing it itself. The agent uses the specspec commandline tools to manipulate the specspec and creates the best implementation-mature version with the given knowledge. The agent commits its changes as "Agent specspec changes: [description]". The agent finally gives a summary of the changes. 


### Implementation

Whenever the specspec is not perfectly implementation-mature, the implementing agent has to close the gap by deepening the specspec by adding conclusion and implementation nodes. The agent never unilaterly adds breadth to or removes from the specspec in an implementation phase. If the implementing agent realizes that there is a contradiction in the spec (or even how to likely improve the product by any means), the agent implements a simple and large-spanning contradiction free subset of the specspec graph and communicates the found contradiction, its subset implementation decisions and the consequences. The agent can also propose a resolution or improvement as a specspec graph on a new proposal branch. 
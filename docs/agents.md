# Project agent instructions

`specspec init` supplies an ordinary root `AGENTS.md` so a newly created graph has
both a manifesto and an explanation of how people/agents should work with it.
[Read the exact shipped template](../src/specspec/templates/AGENTS.md).

## What is in it

- The specification spectrum, all three node types and parent → child justification.
- Intention versus conclusion as a relationship, not a confidence/type field.
- Minimal coherent elements, meaningful splitting/merging and shortcut-free ancestry.
- Positive current binding text, implementation sources and bounded evidence.
- Owner, tandem, agent-planning and implementation phases, with explicit Git control.
- Practical query/ancestor/metric, source, replacement, composition, deletion, repair
  and exact-index checks using the current CLI.

It works for products other than code too. A manifesto states purpose; requirements
state outcomes/constraints/choices; implementation leaves describe actual artifacts.
Nothing in the template makes graph validity a proof of semantic fulfillment.

## Creation and ownership

The template is bundled in the wheel and source distribution and loaded through
Python package resources. No sibling workspace, Git checkout, online download or
working-directory-relative file is needed at runtime.

Initialization validates the manifesto and instruction target, requires Git and
initializes a repository when the directory is not already in a Git working tree.
It stages/journals node and guide bytes under `.specspec/local/` and the workspace
lock. An absent guide is exclusively created; an existing regular file keeps its
exact bytes as the prefix and receives the template after a separating blank line
when needed. Empty and non-UTF-8 prefixes are preserved literally. Directories and
symlinks are rejected rather than followed or silently skipped.

Readable output reports `(created)` or `(template appended)`. Structured receipts
retain `agent_instructions.path` and `created`. This is initialization information,
not graph membership or approval. Re-running init never overwrites an existing
graph; later upgrades do not automatically edit project instructions.

Interrupted initialization uses the same explicit recovery boundary as managed
node writes. A newly created guide is removed on rollback only when its bytes are
still a recognized transaction state. An amended guide rolls back to its exact
original bytes. Intervening owner changes block recovery before any files change.
New-file publication uses exclusive same-filesystem links; existing files use
original-byte checks and staged replacement. Preserve `.specspec/local/` and run
`specspec recover` in the project rather than deleting its journal. Git metadata
created by initialization remains; graph recovery does not remove repositories.

Initialization protects runtime data with a checkout-local Git exclusion, without
changing project ignore rules. It never runs the guide or an agent, stages, commits,
configures identity/hooks or publishes artifacts. Agents still follow the owner's
authorization.

## Owner drafting inputs

The supplied sibling `specspec-agentsmd/` workspace contributed:

- `RESULT_AGENTS.md`: conceptual structure, relationships, granularity, examples and maturity.
- `CLI_COCS_7500.md`: fuller query/source/edit workflow guidance.
- `CLI_COCS_6000.md`: concise CLI wording and priorities.
- This repository's `AGENTS.md`/graph: working phases, owner-change preservation,
  explicit commit boundaries and implementation discipline.

These are design inputs, not runtime dependencies. The shipped text is deliberately
adapted to current behavior: `.specspec/`, ID-only filenames, exact selected deletion
without cascading, safe invalid intermediates, default newline/prose-wrap matching,
and explicit Git authorization. Older draft claims about filename summaries or
all-descendant deletion do not describe the current release. Source-input digests and verification
scope are recorded in the [release investigation](investigations/release-0.1.md).

## Maintaining it

Edit `src/specspec/templates/AGENTS.md`, its specification bindings and tests together.
Build and install a fresh wheel in a disposable environment, initialize a project
outside the checkout and verify the guide. Also rebuild a wheel from the source
distribution. Testing an editable import alone cannot prove the packaged resource
is present. Keep the template generic; repository-specific maintenance belongs in
this checkout's root instructions, not every user's project.

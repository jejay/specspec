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

Initialization validates the candidate, stages/journals bytes under the existing
workspace lock, publishes the graph and exclusively creates the new root guide.
It reports `Agent instructions: AGENTS.md (created)` in readable output; JSON has
`agent_instructions: {"path": "AGENTS.md", "created": true}`. That is initialization
information, not another graph node or approval field. Node format/API remain 7.

If **any entry** already occupies `AGENTS.md`, it is preserved, including empty or
non-UTF-8 files, directories and symlinks. It is not merged, appended to, read as an
instruction source by the CLI or replaced. Output reports preservation (`created:
false`). Integrate the shipped guidance yourself where it fits your project's
instructions. Later CLI upgrades do not overwrite owner-edited guides.

Interrupted initialization uses the same explicit recovery boundary as managed
node writes. A newly created guide is removed on rollback only when its bytes are
still a recognized transaction state. Intervening owner changes block recovery
before any files are changed. Existing guides are never journal-owned. New-file
publication uses an exclusive same-filesystem hard link, then removes its staging
link; unsupported filesystems report a recoverable initialization failure. Preserve
`.specspec-local/` and use `specspec --root PROJECT recover`, rather than deleting it.

The CLI never runs the guide or an agent, initializes Git, stages changes, commits,
installs hooks or publishes artifacts. An agent reading the guide still follows its
operating instructions and the owner's authorization.

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
all-descendant deletion do not describe 0.1. Source-input digests and verification
scope are recorded in the [release investigation](investigations/release-0.1.md).

## Maintaining it

Edit `src/specspec/templates/AGENTS.md`, its specification bindings and tests together.
Build and install a fresh wheel in a disposable environment, initialize a project
outside the checkout and verify the guide. Also rebuild a wheel from the source
distribution. Testing an editable import alone cannot prove the packaged resource
is present. Keep the template generic; repository-specific maintenance belongs in
this checkout's root instructions, not every user's project.

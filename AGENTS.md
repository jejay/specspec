# Working on SpecSpec

## Project specification

The active specification is the tool-managed graph in `_specspec/`. Read
`docs/own-spec.md` for the entry points and review status of the migrated nodes.
`INTENTION_SPEC.md` is the user's original source; `CONCLUSION_SPEC.md` records
technical proposals. Neither document automatically approves every graph node.

Use the installed CLI, or `python -m specspec` in the development environment:

```sh
python -m specspec list --json
python -m specspec context <node-id> --json
python -m specspec impact <node-id> --json
```

Before changing code, read the relevant node and its ancestors. Treat proposed
nodes as candidates, not user-approved constraints. Existing code and passing
tests do not turn a proposal into an accepted decision.

## Changes

- Do not edit node Markdown/frontmatter directly or recompute integrity hashes
  outside the tool. Use `add`, `update`, `accept`, and `retire`.
- Use `--expect <fingerprint>` when applying changes against a displayed snapshot.
- Propose a separate conclusion when a change introduces a meaningful choice.
  Do not rewrite its parent intention to make a chosen implementation inevitable.
- Accept newly proposed decisions only with explicit user authorization.
- Keep implementation explanations and `sources` references current when code
  or verification changes. Source symbols are descriptive, not machine-resolved.
- Present specification changes, code changes, and affected nodes together.
- Never silently stage files, create commits, or install/replace local Git hooks.

## Checks

```sh
python -m specspec validate --warnings-as-errors
python -m ruff check .
python -m ruff format --check .
python -m pytest
npm --prefix vscode test
```

Use `python -m specspec diff --base HEAD --json` for a review report. Before a
commit, stage the complete intended graph change and use `hook check` to validate
that exact index; working-tree validation cannot substitute for staged validation.

If an edit is interrupted, retain `.specspec-local/` and run `recover`. Remove a
stale lock with `recover --force-lock` only after confirming no writer is running.

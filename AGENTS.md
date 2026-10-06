# Working on SpecSpec

## Project specification and review

The active specification is the tool-managed graph in `_specspec/`. Read
`docs/own-spec.md` for entry points, current choices, and withdrawn design history.
`INTENTION_SPEC.md` is the user's original source; `CONCLUSION_SPEC.md` records
technical conclusions. The graph also records the user's later corrections.

Use the installed CLI, or `python -m specspec` in the development environment:

```sh
python -m specspec list --json
python -m specspec context <node-id> --json
python -m specspec impact <node-id> --json
```

Before changing code, read the relevant node and its ancestors. Distinguish core
intentions from revisable conclusions by their relationships and explanations,
not proposed/accepted statuses. Review is risk-proportionate: earlier intentions
will often receive more attention, but depth is not a confidence score or a review
quota. When the user considers an implementation attempt worth its uncertainty and
token cost, there is no additional per-node approval ceremony before proceeding.

Keep conclusions revisable. Working code and passing tests are evidence, not proof
of correctness or a reason to silently rewrite the user's intentions. Surface
material uncertainty and conflicts rather than manufacturing agreement.

## Changes

- Do not edit node Markdown/frontmatter directly or recompute integrity hashes
  outside the tool. Use `add`, `update`, `retire`, `restore`, and `migrate`.
- Use `--expect <fingerprint>` when applying changes against a displayed snapshot.
- Record a separate conclusion when a change introduces a meaningful choice.
  Do not rewrite its parent intention to make a chosen implementation inevitable.
- Do not introduce approval statuses, acceptance scores, or parent-review gates.
  Git differences communicate newness and change relative to the selected base.
- Retirement means withdrawal with retained history, not insufficient review.
  Keep live nodes independent of retired parents; restoration is not approval.
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

Use `python -m specspec diff --base HEAD --json` for a review report. Before an
explicitly authorized commit, stage the complete intended graph change and use
`hook check` to validate that exact index; working-tree validation cannot
substitute for staged validation.

The current writer uses format/API version 2. Older Git revisions remain readable;
convert a valid v1 workspace with `migrate --expect <fingerprint>` before editing.
Migration verifies its original integrity and journals the whole conversion.

If an edit is interrupted, retain `.specspec-local/` and run `recover`. Remove a
stale lock with `recover --force-lock` only after confirming no writer is running.

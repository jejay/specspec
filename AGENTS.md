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

- Use `add`, `update`, `retire`, and `restore` for ordinary canonical graph changes
  in this checkout. The product permits manual Markdown edits, but CLI/UI editing
  remains recommended. Format/API 4 has no node hashes, fingerprints, or `--expect`; source blob IDs
  are Git content addresses, not node edit gates.
  The authorized compact-ID conversion is a one-time tool-managed migration,
  not a permanent compatibility command.
- Record a separate conclusion when a change introduces a meaningful choice.
  Do not rewrite its parent intention to make a chosen implementation inevitable.
- Do not introduce approval statuses, acceptance scores, or parent-review gates.
  Git differences communicate newness and change relative to the selected base.
- Retirement means withdrawal with retained history, not insufficient review.
  Keep live nodes independent of retired parents; restoration is not approval.
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
python -m specspec validate --warnings-as-errors
python -m ruff check .
python -m ruff format --check .
python -m pytest
npm --prefix graph-ui-common test
npm --prefix vscode test
npm --prefix electron test
```

Use `python -m specspec diff --base <current-scheme-ref> --json` for a review report
when the baseline uses the current schema. Before an explicitly authorized commit,
stage the complete intended graph change and use `hook check` to validate that exact
index; working-tree validation cannot substitute for staged validation.

Maintain only the current schema: padded Base64url IDs over five random bytes,
including the final `=`, and `<id><slug>.md` filenames. Do not retain overwritten
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
and additional examples as if all revisions had always used today's SpecSpec.
Refresh all retained refs, withdrawn nodes, actual receipts, commit ledgers, bundle
and tracked snapshot together; validate every revision with current tools. Updating
only HEAD or retaining old readers is not a solution. See
`example/gantt/history/WALKTHROUGH.md`. Preserve local experiments before explicitly
recreating stale clones; never reset them silently or rewrite unrelated SpecSpec
history. Plausible graph emergence/revision is sufficient; fabricated AI dialogue
is not required. Focused unit tests may use smaller independent current-schema graphs.

If an edit is interrupted, retain `.specspec-local/` and run `recover`. Remove a
stale lock with `recover --force-lock` only after confirming no writer is running.

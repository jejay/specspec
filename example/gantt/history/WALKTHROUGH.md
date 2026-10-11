# Inspect the maintained Gantt Git history

This project is the current-schema Git regression corpus. Its complete independent
history is in `gantt.bundle`: three spec-before-code stage pairs, an empty predecessor
and a final audit. The history was deliberately rebuilt under the current SpecSpec
scheme. CLI receipts are new executions, not edited API-2 receipts or invented
original evidence. Unrelated SpecSpec development history was not rewritten.

From the SpecSpec repository root, with its development Python active:

```sh
git clone example/gantt/history/gantt.bundle ../gantt-history
python -m specspec --root ../gantt-history validate --warnings-as-errors
python -m specspec --root ../gantt-history diff \
  --base stage/01-code --target stage/02-spec --json
python -m specspec --root ../gantt-history diff \
  --base stage/02-code --target stage/03-spec --json
git -C ../gantt-history log --oneline --all
```

The first redirect withdraws 13 of 17 live nodes; the second withdraws 9 of 16.
Bodies, IDs, parents and source references of those withdrawn branches remain
unchanged apart from the withdrawal flag. The new workshop weekday choice has a
new identity and justification, not restoration/approval of the portfolio choice.

`revisions.json` records actual predecessor/spec/code commit IDs and CLI receipt
ordinals. All node IDs are eight-character padded Base64url strings, including `=`.
There are no stored graph fingerprints, old metadata normalization or `--expect`.

## Run a historical prototype separately

Worktrees are explicit opt-in operations in your disposable clone:

```sh
git -C ../gantt-history worktree add --detach ../gantt-portfolio stage/01-code
node --test ../gantt-portfolio/test/model.test.cjs
git -C ../gantt-history worktree add --detach ../gantt-personal stage/02-code
node --test ../gantt-personal/test/model.test.cjs
# Open each worktree's index.html, or serve that folder locally.
git -C ../gantt-history worktree remove ../gantt-portfolio
git -C ../gantt-history worktree remove ../gantt-personal
```

Stage one has six model tests, stage two seven, stage three twenty. Spec checkpoints
still contain the preceding runnable app, except the first which has no app code.
Application JSON v1 conversion remains a workshop feature; it is not support for an
obsolete SpecSpec schema. Old node schemas are intentionally not supported.

## Verify the entire fixture

```sh
python example/gantt/history/verify.py --history
```

The verifier clones the bundle temporarily. It checks every commit's current
schema/DAG, the final exact index, actual receipt/context/impact results, stage
ordering, semantic/edge/source diffs and both withdrawal sets; it runs all three
stages' Node model tests. Repository pytest adds exact-index/partial-staging,
rename/source/removed-edge and other Git regressions on current graphs.

The root SpecSpec graph is self-referencing evolving design documentation. Its
obsolete revisions are not required to render or validate with current tooling.
Do not add old-schema readers merely to keep comparisons of that history working.

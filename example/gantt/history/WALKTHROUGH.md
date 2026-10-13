# Inspect the independent Gantt Git history

## Why comparisons in `example/gantt` can fail

The **tracked** `example/gantt` folder is a fixture snapshot in the SpecSpec
checkout, not an independent Git working repository. Git there finds the enclosing
SpecSpec repository, including old node formats. Selecting its old commits in the
UI can therefore fail schema validation. This is expected: current tooling must
not retain old readers just to understand SpecSpec development history.

The complete, **independent** example history lives in `gantt.bundle`. It has eight
commits: an empty predecessor, three spec-before-code pairs and a final audit.
Every nonempty revision uses the current node schema. Clone it outside the
SpecSpec worktree and open **that clone** in VS Code or Electron for Git experiments.
Do not add `.git` to the tracked snapshot or compare obsolete parent-repository refs.

## Create a manual example workspace

From the SpecSpec repository root, with its development Python active:

```sh
python example/gantt/history/checkout.py
```

The default destination is `~/Projects/specspec-examples/gantt`, or
`~\Projects\specspec-examples\gantt` on Windows. An explicit destination is allowed:

```sh
python example/gantt/history/checkout.py ../specspec-examples/gantt
```

The helper refuses existing destinations (including empty folders) and destinations
inside the development Git worktree. It never resets experiments, installs hooks,
stages files or commits. LF checkout configuration is persisted in the clone.
The tracked bundle stays portable; tests and CI do not depend on your manual clone.

From the new example folder:

```sh
git rev-parse --show-toplevel  # Must be this example folder, not SpecSpec.
git log --oneline --all
python -m specspec validate --warnings-as-errors
python -m specspec diff --base stage/01-code --target stage/02-spec --json
python -m specspec diff --base stage/02-code --target stage/03-spec --json
```

In the graph UI, choose the clone as the project, then **Compare Revisions** with
those same base/target tags. `HEAD` is the final audit; an empty target compares
against this clone's worktree. Do not reuse hashes from the old development history.
`revisions.json` records actual predecessor/spec/code commit IDs and receipt ordinals.
The tags are readable stage names, not node approval states.

The first redirect deletes 13/17 nodes; the second deletes 9/16. Their files are
physically absent after each redirect and their original IDs, bodies, parents and
sources remain in the predecessor commits. Each redirect commit explains why.
Default workspace always compares to HEAD: D ghosts survive staging, then vanish
after commit without a retired/restore workflow. Workshop weekday reasoning is a
new justification, not approval or resurrection of the portfolio branch. `cli.jsonl` contains new actual executions from reconstruction, not
altered older receipts or a claim that original commits used today's encoding.

## Run historical prototypes separately

From your clone, worktrees are explicit opt-in operations:

```sh
git worktree add --detach ../gantt-portfolio stage/01-code
node --test ../gantt-portfolio/test/model.test.cjs
git worktree add --detach ../gantt-personal stage/02-code
node --test ../gantt-personal/test/model.test.cjs
# Open each worktree's index.html, or serve that folder locally.
git worktree remove ../gantt-portfolio
git worktree remove ../gantt-personal
```

The stages have six, seven and twenty model tests. Spec checkpoints retain the
previous prototype; the first has no app code. App JSON v1 conversion is a workshop
feature, **not** compatibility with obsolete SpecSpec node schemas.

## Verify the maintained corpus

From the SpecSpec checkout:

```sh
python example/gantt/history/verify.py --history
python -m pytest tests/test_example_checkout.py tests/test_gantt_example.py tests/test_gantt_git.py
```

The verifier clones temporarily and checks **all retained refs/commits**, current
schema/DAG, independent Git/index, tags, actual receipt/context/impact contents,
stage ordering, both deletion sets/reasons, semantic/edge/source diffs and all runnable
model stages. It compares the final runtime/tests and graph with the tracked
snapshot to catch drift. Git integration and real-host fixtures use the same clone
helper; host fixtures add disposable A/M/D worktree changes without discarding
history. CI runs the final model/browser app in an independent clone. Focused unit
fixtures may be smaller independently generated current-schema projects. No test
requires obsolete SpecSpec development revisions or a full root-history fetch.

## Every schema change requires a full example-history rewrite

This is a **recurring maintenance obligation**, not a one-time ID conversion:

1. Build a fresh independent repository outside SpecSpec. Do not merely update
   `HEAD`, add a migration commit, or leave old-format branches/tags reachable.
2. Reconstruct the example's entire chronological graph/code evolution using the
   current CLI/schema, as if it had always been developed with today's SpecSpec.
   Use one consistent identity mapping through all revisions; convert every
   parent, filename, embedded reference and earlier/deleted node as needed. Revise
   schema/API-specific operations and verification, not the app's core intentions.
3. Preserve plausible graph emergence, revisable conclusions, substantial
   redirects, deletion reasons/earlier reasoning in Git and spec-before-code boundaries.
   **No invented AI conversation is required.** Optional fictional stories are
   illustrations, not authorization or evidence. Execute checks and CLI operations
   for real; regenerate receipts instead of editing old outputs to look current.
4. Validate every retained revision/ref and exact staged graphs with current
   tooling; run historical apps/tests and temporal comparisons. Recreate stage
   tags and update all commit IDs, receipt ordinals and ledgers. Use a fresh repo
   without inherited old refs; do not archive obsolete schema refs in the corpus.
5. Export a complete, prerequisite-free bundle, e.g. `git -C <fresh-example>
   bundle create <SpecSpec>/example/gantt/history/gantt.bundle --all`. Refresh
   the tracked current graph/runtime/receipts/ledger and applicable docs together.
   Do not include the bundle inside its own history. Run the verifier and all
   integration suites against this new bundle before treating it as maintained.
6. Existing manual clones are intentionally **not reset automatically**. Save any
   local experiments, then explicitly recreate the workspace at a new destination
   (or remove the old clone yourself). Old hashes no longer identify maintained
   stages. Never rewrite or force-push unrelated SpecSpec development history.

This policy applies to Gantt and any additional maintained example repositories.
The backend remains current-only; fixture reconstruction is development work,
not a production legacy-reader/migration feature. SpecSpec's own graph continues
to receive present-working-graph and source-reference validation.

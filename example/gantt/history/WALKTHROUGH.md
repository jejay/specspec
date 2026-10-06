# Inspect the evolution, don't blindly replay it

All commands below are from the SpecSpec repository root with the development
Python environment active. These are inspection commands; canonical changes have
already happened. The recorded CLI argv/stdin in `cli.jsonl` are receipts, **not** a
script to replay against an existing graph. IDs and fingerprints are real snapshots.

## Find the commits

```sh
git log --oneline -- example/gantt
git show 3ba86c0:example/gantt/STORY.md
git show 8ac5676:example/gantt/model.js
git show f54142a:example/gantt/model.js
```

`revisions.json` holds full SHAs and graph fingerprints for all three spec/code
pairs. Each spec is committed before its implementation. The final audit records
the last implementation's hash after it exists; there is no circular self-hash.

## Compare both major redirects without checkout

```sh
python -m specspec --root example/gantt diff --base 8ac5676 --target f656942 --json
# 13 retained nodes acquire withdrawal flags, 10 new intention/choice nodes.
python -m specspec --root example/gantt diff --base f54142a --target 95be927 --json
# 9 retained nodes acquire withdrawal flags, 12 new intention/choice nodes.
python -m specspec --root example/gantt list --retired --json
python -m specspec --root example/gantt context beb1f8f3-aafe-4f77-83fb-9d1ffc9b3baa --include-retired --json
```

The original weekday/portfolio conclusion remains withdrawn. Similar new workshop
reasoning is a new identity with different justifications, not silent restoration.
A live node never depends on a withdrawn parent; old branches were retired as whole
explicitly named batches after reading impact. Their body/source/parent semantics
were not rewritten. Withdrawal is not insufficient review or a node-approval stage.

## Run a historical prototype separately

Keep your current tree intact. Git worktrees here are **opt-in commands for you**;
creating the example did not silently create worktrees or branches:

```sh
git worktree add --detach ../gantt-portfolio 8ac5676
# Open ../gantt-portfolio/example/gantt/index.html, or serve that folder.
node --test ../gantt-portfolio/example/gantt/test/*.test.cjs
git worktree add --detach ../gantt-personal f54142a
node --test ../gantt-personal/example/gantt/test/*.test.cjs
# Remove only those disposable worktrees when finished:
git worktree remove ../gantt-portfolio
git worktree remove ../gantt-personal
```

The first graph commit has no app code; the first runnable experiment has six model
tests. The manual prototype has seven. The final workshop has twenty plus an
optional installed-browser harness. Old prototypes explicitly did not claim browser,
cloud, authentication, or resource-optimization evidence.

## How the managed edits were performed

For a new project, the agent starts with a supplied manifesto body and `init`.
For each intention or separate conclusion it displays a fresh snapshot, then:

```sh
# Illustrative placeholders, not commands to paste into this existing example:
python -m specspec --root <project> add --parent <id> --slug <summary> \
  --body <body-file> --expect <displayed-fingerprint> --json
python -m specspec --root <project> context <new-id> --json
python -m specspec --root <project> impact <obsolete-intention-id> --json
python -m specspec --root <project> retire <complete-obsolete-dependent-set> \
  --expect <fresh-fingerprint> --json
```

Meaningful choices have their own requirement nodes and explanatory origins;
implementation nodes are terminal and link actual files. User/AI roles and stage
numbers are narrative text, not a custom frontmatter taxonomy. The agent did not
handwrite canonical node files, recompute hashes, stage unrelated files, install
hooks, or fabricate/backdate commits. Verify the receipts/history with:

```sh
python example/gantt/history/verify.py --history
```
